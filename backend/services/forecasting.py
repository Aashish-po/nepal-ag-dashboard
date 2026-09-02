"""
Forecasting service — SARIMAX / ExponentialSmoothing model selection and inference.

Trains univariate time-series models on historical yield data and writes
pre-computed forecasts into the ``forecasts`` table so the API endpoint can
serve them without latency spikes on every request.

Model selection strategy (AIC-based):
  1. Fit a SARIMAX(1,0,0) with seasonal order (1,0,0,12).
  2. Fit an ExponentialSmoothing trend='add', seasonal='add', period=12.
  3. Pick the model with the lower AIC; fall back to ES if SARIMA fails.

Outputs are cached in the ``forecasts`` table keyed by
(district_id, crop_id, forecast_month, forecast_model), so re-running the
training job is idempotent — existing rows are upserted.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #


class _FitResult:
    """Internal container for fitted-model outputs."""

    __slots__ = ("aic", "ci_width", "forecast", "mae", "mape", "rmse")

    def __init__(
        self,
        forecast: list[float],
        ci_width: list[float],
        aic: float,
        rmse: float,
        mae: float,
        mape: float,
    ) -> None:
        self.forecast = forecast
        self.ci_width = ci_width
        self.aic = aic
        self.rmse = rmse
        self.mae = mae
        self.mape = mape


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def train_district_crop_forecast(
    db: Session,
    district_id: int,
    crop_id: int,
    months_ahead: int = 12,
) -> int:
    """Train a forecast model for one district×crop pair and persist results.

    Args:
        db: SQLAlchemy session.
        district_id: Target district.
        crop_id: Target crop.
        months_ahead: Forecast horizon (1–36).

    Returns:
        Number of forecast rows written (should be ``months_ahead`` on success).
    """
    yield_rows = _fetch_yield_series(db, district_id, crop_id)
    if len(yield_rows) < 5:
        logger.warning(
            "Skipping district=%s crop=%s: only %d years of yield data",
            district_id,
            crop_id,
            len(yield_rows),
        )
        return 0

    values = np.array([float(r.yield_kg_ha or 0) for r in yield_rows], dtype=float)
    years = [int(r.year) for r in yield_rows]
    # Build a monthly frequency series: repeat each annual value across 12
    # months so seasonal models have enough observations.
    monthly_series = _build_monthly_from_annual(years, values)

    result = _select_model(monthly_series)
    if result is None:
        logger.warning(
            "No model could be fit for district=%s crop=%s", district_id, crop_id
        )
        return 0

    now = datetime.now(tz=timezone.utc)
    forecast_start = date(now.year, now.month, now.day) + timedelta(days=1)
    records: list[dict[str, Any]] = []
    for i in range(months_ahead):
        future_date = forecast_start + timedelta(days=30 * (i + 1))
        forecast_date = date(future_date.year, future_date.month, 1)
        point_pred = float(result.forecast[i])
        spread = float(result.ci_width[i])
        records.append(
            {
                "district_id": district_id,
                "crop_id": crop_id,
                "forecast_month": forecast_date,
                "forecast_yield_kg_ha": round(point_pred, 2),
                "lower_ci_95": round(max(0.0, point_pred - spread), 2),
                "upper_ci_95": round(point_pred + spread, 2),
                "forecast_model": result.model_name,
                "forecast_date": now,
                "rmse_kg_ha": round(result.rmse, 2),
                "mae_kg_ha": round(result.mae, 2),
                "mape_pct": round(result.mape, 2),
            }
        )

    _upsert_forecasts(db, records)
    logger.info(
        "Trained %s for district=%s crop=%s → %d rows",
        result.model_name,
        district_id,
        crop_id,
        len(records),
    )
    return len(records)


def train_all_forecasts(db: Session, months_ahead: int = 12) -> dict[str, int]:
    """Train forecasts for every district×crop combination with sufficient data.

    Args:
        db: SQLAlchemy session.
        months_ahead: Forecast horizon per pair.

    Returns:
        Dict mapping district_id (as string) → rows written.
    """
    from api.models.db_models import Yields

    combos_stmt = (
        select(Yields.district_id, Yields.crop_id)
        .where(Yields.yield_kg_ha.isnot(None))
        .distinct()
    )
    rows = db.execute(combos_stmt).all()

    results: dict[str, int] = {}
    for district_id, crop_id in rows:
        try:
            n = train_district_crop_forecast(
                db, int(district_id), int(crop_id), months_ahead
            )
        except Exception as exc:  # noqa: BLE001 — never let one bad combo kill the job
            logger.warning(
                "Forecast failed for district=%s crop=%s: %s", district_id, crop_id, exc
            )
            n = 0
        if n > 0:
            results[str(district_id)] = results.get(str(district_id), 0) + n

    total = sum(results.values())
    logger.info(
        "train_all_forecasts complete: %d district×crop pairs, %d rows written",
        len(results),
        total,
    )
    return results


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _fetch_yield_series(db: Session, district_id: int, crop_id: int) -> list[Any]:
    """Fetch ordered yield records for one district×crop pair."""
    from api.models.db_models import Yields

    stmt = (
        select(Yields.year, Yields.yield_kg_ha)
        .where(Yields.district_id == district_id)
        .where(Yields.crop_id == crop_id)
        .where(Yields.yield_kg_ha.isnot(None))
        .order_by(Yields.year)
    )
    rows = db.execute(stmt).all()

    # Inline helper avoids a module-level class for this ad-hoc accessor.
    def _attr(row: Any, name: str, *, default: Any = None) -> Any:
        """Return an attribute if present; otherwise fall back to a default."""
        if hasattr(row, name):
            return getattr(row, name)
        return default

    return [
        type(
            "YieldRecord",
            (),
            {
                "year": _attr(r, "year"),
                "yield_kg_ha": _attr(r, "yield_kg_ha"),
            },
        )()
        for r in rows
    ]


def _build_monthly_from_annual(years: list[int], values: np.ndarray) -> pd.Series:
    """Upsample annual yields to monthly by repeating each value 12 times."""
    records: list[tuple[date, float]] = []
    for yr, val in zip(years, values):
        for month in range(1, 13):
            records.append((date(yr, month, 1), float(val)))
    idx = pd.DatetimeIndex([d for d, _ in records])
    return pd.Series([v for _, v in records], index=idx)


class _ModelResult:
    """Internal container for selected-model output."""

    __slots__ = ("ci_width", "forecast", "mae", "mape", "model_name", "rmse")

    def __init__(
        self,
        model_name: str,
        forecast: list[float],
        ci_width: list[float],
        rmse: float,
        mae: float,
        mape: float,
    ) -> None:
        self.model_name = model_name
        self.forecast = forecast
        self.ci_width = ci_width
        self.rmse = rmse
        self.mae = mae
        self.mape = mape


def _select_model(series: pd.Series) -> _ModelResult | None:
    """Fit SARIMA and ExponentialSmoothing, return the better result by AIC."""
    sarima_result = None
    es_result = None
    try:
        sarima_result = _fit_sarimax(series)
    except Exception:
        logger.debug("SARIMAX fit failed via wrapper", exc_info=True)
    try:
        es_result = _fit_es(series)
    except Exception:
        logger.debug("ExponentialSmoothing fit failed via wrapper", exc_info=True)
    candidates: list[tuple[str, _FitResult | None]] = [
        ("SARIMAX", sarima_result),
        ("ExponentialSmoothing", es_result),
    ]
    best_name, best_fit = min(
        candidates,
        key=lambda x: x[1].aic if x[1] is not None else float("inf"),
    )
    if best_fit is None:
        return None
    return _ModelResult(
        model_name=best_name,
        forecast=best_fit.forecast,
        ci_width=best_fit.ci_width,
        rmse=best_fit.rmse,
        mae=best_fit.mae,
        mape=best_fit.mape,
    )


def _fit_sarimax(
    series: pd.Series,
) -> _FitResult | None:  # pragma: no cover — statsmodels
    try:
        from statsmodels.tsa.statespace.sarimax import (
            SARIMAX,  # type: ignore[import-untyped]
        )

        model = SARIMAX(
            series,
            order=(1, 0, 0),
            seasonal_order=(1, 0, 0, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fit = model.fit(disp=False, maxiter=200)
        steps = min(36, len(series))
        pred = fit.get_forecast(steps=steps)  # type: ignore[union-attr]
        mean = pred.predicted_mean
        ci = pred.conf_int(alpha=0.05)
        split = int(len(series) * 0.8)
        if split > 5:
            train = series.iloc[:split]
            test = series.iloc[split:]
            refit = SARIMAX(
                train,
                order=(1, 0, 0),
                seasonal_order=(1, 0, 0, 12),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False, maxiter=200)
            predicted = refit.get_forecast(steps=len(test)).predicted_mean.values  # type: ignore[union-attr]
            actual = test.values
            residuals = actual - predicted
            rmse = float(np.sqrt(np.mean(residuals**2)))
            mae = float(np.mean(np.abs(residuals)))
            nonzero_mask = actual != 0
            nonzero = actual[nonzero_mask]
            mape = (
                float(np.mean(np.abs(residuals[nonzero_mask] / nonzero)) * 100)
                if len(nonzero) > 0  # type: ignore[arg-type]
                else 0.0
            )
        else:
            rmse = mae = mape = 0.0
        return _FitResult(
            forecast=mean.values.tolist(),  # type: ignore[attr-defined]
            ci_width=((ci.iloc[:, 1] - ci.iloc[:, 0]) / 2).values.tolist(),  # type: ignore[attr-defined]
            aic=float(fit.aic),  # type: ignore[attr-defined]
            rmse=rmse,
            mae=mae,
            mape=mape,
        )
    except Exception:  # noqa: BLE001 — SARIMAX may fail on short/noisy series
        logger.debug("SARIMAX fit failed")
        return None


def _fit_es(series: pd.Series) -> _FitResult | None:  # pragma: no cover — statsmodels
    try:
        from statsmodels.tsa.holtwinters import (
            ExponentialSmoothing,  # type: ignore[import-untyped]
        )

        model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal="add",
            seasonal_periods=12,
        )
        fit = model.fit(optimized=True)
        steps = min(36, len(series))
        pred = fit.forecast(steps=steps)  # type: ignore[union-attr]
        residuals = fit.resid.dropna()  # type: ignore[attr-defined]
        resid_std = float(residuals.std()) if len(residuals) > 2 else 0.0
        ci_width = [resid_std * (1 + 0.05 * h) for h in range(1, steps + 1)]
        split = int(len(series) * 0.8)
        if split > 5:
            train = series.iloc[:split]
            test = series.iloc[split:]
            refit = ExponentialSmoothing(
                train, trend="add", seasonal="add", seasonal_periods=12
            ).fit(optimized=True)
            predicted = refit.forecast(len(test)).values  # type: ignore[union-attr]
            actual = test.values
            residuals = actual - predicted
            rmse = float(np.sqrt(np.mean(residuals**2)))
            mae = float(np.mean(np.abs(residuals)))
            nonzero_mask = actual != 0
            nonzero = actual[nonzero_mask]
            mape = (
                float(np.mean(np.abs(residuals[nonzero_mask] / nonzero)) * 100)
                if len(nonzero) > 0  # type: ignore[arg-type]
                else 0.0
            )
        else:
            rmse = mae = mape = 0.0
        return _FitResult(
            forecast=pred.values.tolist(),  # type: ignore[attr-defined]
            ci_width=ci_width,
            aic=float(fit.aic),  # type: ignore[attr-defined]
            rmse=rmse,
            mae=mae,
            mape=mape,
        )
    except Exception:  # noqa: BLE001 — ExponentialSmoothing may fail on edge cases
        logger.debug("ExponentialSmoothing fit failed")
        return None


def _upsert_forecasts(db: Session, records: list[dict[str, Any]]) -> None:
    """Bulk upsert forecast rows, keyed by (district_id, crop_id, forecast_month, forecast_model)."""
    from api.models.db_models import Forecasts
    from sqlalchemy import insert

    try:
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        pg_stmt = pg_insert(Forecasts).values(records)  # type: ignore[arg-type]
        upsert = pg_stmt.on_conflict_do_update(
            index_elements=[
                "district_id",
                "crop_id",
                "forecast_month",
                "forecast_model",
            ],
            set_={
                "forecast_yield_kg_ha": pg_stmt.excluded.forecast_yield_kg_ha,
                "lower_ci_95": pg_stmt.excluded.lower_ci_95,
                "upper_ci_95": pg_stmt.excluded.upper_ci_95,
                "rmse_kg_ha": pg_stmt.excluded.rmse_kg_ha,
                "mae_kg_ha": pg_stmt.excluded.mae_kg_ha,
                "mape_pct": pg_stmt.excluded.mape_pct,
                "forecast_date": pg_stmt.excluded.forecast_date,
            },
        )
        db.execute(upsert)
    except Exception:  # noqa: BLE001 — SQLite has no on_conflict_do_update
        stmt = insert(Forecasts).values(records)  # type: ignore[arg-type]
        db.execute(stmt)
    db.commit()
