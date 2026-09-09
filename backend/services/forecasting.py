"""
Forecasting service — SARIMAX / ExponentialSmoothing model selection and inference.

Trains univariate time-series models on historical yield data and writes
pre-computed forecasts into the ``forecasts`` table so the API endpoint can
serve them without latency spikes on every request.

Model selection strategy (AIC-based):
  1. Fit a SARIMAX(1,0,0) with seasonal order (1,0,0,12).
  2. Fit an ExponentialSmoothing trend='add', seasonal='add', period=12.
  3. Pick the model with the lower AIC; fall back to ES if SARIMA fails.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

import numpy as np
import pandas as pd
from api.models.db_models import MIN_FORECAST_HISTORY_YEARS
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def train_district_crop_forecast(
    db: Session,
    district_id: int,
    crop_id: int,
    months_ahead: int = 12,
) -> int:
    """Train a forecast model for one district×crop pair and persist results."""
    yield_rows = _fetch_yield_series(db, district_id, crop_id)
    if len(yield_rows) < MIN_FORECAST_HISTORY_YEARS:
        logger.warning(
            "Skipping district=%s crop=%s: only %d years of yield data (need >= %s)",
            district_id,
            crop_id,
            len(yield_rows),
            MIN_FORECAST_HISTORY_YEARS,
        )
        return 0

    values = np.array([float(r.yield_kg_ha or 0) for r in yield_rows], dtype=float)
    years = [int(r.year) for r in yield_rows]
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
        point_pred = float(result["forecast"][i])
        spread = float(result["ci_width"][i])
        records.append(
            {
                "district_id": district_id,
                "crop_id": crop_id,
                "forecast_month": forecast_date,
                "forecast_yield_kg_ha": round(point_pred, 2),
                "lower_ci_95": round(max(0.0, point_pred - spread), 2),
                "upper_ci_95": round(point_pred + spread, 2),
                "forecast_model": result["model_name"],
                "forecast_date": now,
                "rmse_kg_ha": round(result["rmse"], 2),
                "mae_kg_ha": round(result["mae"], 2),
                "mape_pct": round(result["mape"], 2),
            }
        )

    _upsert_forecasts(db, records)
    logger.info(
        "Trained %s for district=%s crop=%s → %d rows",
        result["model_name"],
        district_id,
        crop_id,
        len(records),
    )
    return len(records)


def train_all_forecasts(db: Session, months_ahead: int = 12) -> dict[str, int]:
    """Train forecasts for every district×crop combination with sufficient data."""
    from api.models.db_models import Yields

    combos = db.execute(
        select(Yields.district_id, Yields.crop_id)
        .where(Yields.yield_kg_ha.isnot(None))
        .distinct()
    ).all()

    results: dict[str, int] = {}
    for district_id, crop_id in combos:
        try:
            n = train_district_crop_forecast(
                db, int(district_id), int(crop_id), months_ahead
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Forecast failed for district=%s crop=%s: %s", district_id, crop_id, exc
            )
            if "years of yield data" in str(exc):
                logger.info("  -> reason: insufficient historical data")
            elif "model" in str(exc).lower() or "fit" in str(exc).lower():
                logger.info("  -> reason: model fit failed")
            else:
                logger.info("  -> reason: %s", type(exc).__name__)
            n = 0
        if n > 0:
            results[str(district_id)] = results.get(str(district_id), 0) + n

    logger.info(
        "train_all_forecasts complete: %d pairs, %d rows written",
        len(results),
        sum(results.values()),
    )
    return results


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


@dataclass
class _YieldPoint:
    year: int
    yield_kg_ha: float | None


def _fetch_yield_series(
    db: Session, district_id: int, crop_id: int
) -> list[_YieldPoint]:
    """Fetch ordered yield records for one district×crop pair."""
    from api.models.db_models import Yields

    rows = db.execute(
        select(Yields.year, Yields.yield_kg_ha)
        .where(Yields.district_id == district_id)
        .where(Yields.crop_id == crop_id)
        .where(Yields.yield_kg_ha.isnot(None))
        .order_by(Yields.year)
    ).all()
    return [
        _YieldPoint(year=int(r.year), yield_kg_ha=float(r.yield_kg_ha or 0))
        for r in rows
    ]


def _build_monthly_from_annual(years: list[int], values: np.ndarray) -> pd.Series:
    """Upsample annual yields to monthly by repeating each value 12 times."""
    dates = [date(y, m, 1) for y in years for m in range(1, 13)]
    return pd.Series(
        np.repeat(values, 12),
        index=pd.DatetimeIndex(dates),
    )


def _metrics(actual: np.ndarray, predicted: np.ndarray) -> tuple[float, float, float]:
    """Compute RMSE, MAE, MAPE from actual vs predicted arrays."""
    actual_arr = np.asarray(actual, dtype=float)
    predicted_arr = np.asarray(predicted, dtype=float)
    residuals = actual_arr - predicted_arr
    rmse = float(np.sqrt(np.mean(residuals**2)))
    mae = float(np.mean(np.abs(residuals)))
    nonzero = actual_arr[actual_arr != 0]
    mape = (
        float(np.mean(np.abs(residuals[actual_arr != 0] / nonzero)) * 100)
        if len(nonzero)
        else 0.0
    )
    return rmse, mae, mape


def _select_model(series: pd.Series) -> dict[str, Any] | None:
    """Fit SARIMA and ExponentialSmoothing, return the better result by AIC."""
    sarima = _fit_sarimax_safe(series)
    es = _fit_es_safe(series)
    candidates = [("SARIMAX", sarima), ("ExponentialSmoothing", es)]
    best_name, best = min(
        candidates, key=lambda x: x[1]["aic"] if x[1] else float("inf")
    )
    if best is None:
        return None
    return {
        "model_name": best_name,
        "forecast": best["forecast"],
        "ci_width": best["ci_width"],
        "rmse": best["rmse"],
        "mae": best["mae"],
        "mape": best["mape"],
    }


def _fit_sarimax_safe(series: pd.Series) -> dict[str, Any] | None:
    try:
        return _fit_sarimax(series)
    except Exception:
        logger.debug("SARIMAX fit failed", exc_info=True)
        return None


def _fit_es_safe(series: pd.Series) -> dict[str, Any] | None:
    try:
        return _fit_es(series)
    except Exception:
        logger.debug("ExponentialSmoothing fit failed", exc_info=True)
        return None


def _fit_sarimax(
    series: pd.Series,
) -> dict[str, Any] | None:
    from statsmodels.tsa.statespace.sarimax import (
        SARIMAX,
    )

    try:
        model = SARIMAX(
            series,
            order=(1, 0, 0),
            seasonal_order=(1, 0, 0, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fit: Any = model.fit(disp=False, maxiter=200)
        steps = min(36, len(series))
        pred = fit.get_forecast(steps=steps)
        ci = pred.conf_int(alpha=0.05)
        split = int(len(series) * 0.8)
        if split > 5:
            train, test = series.iloc[:split], series.iloc[split:]
            refit: Any = SARIMAX(
                train,
                order=(1, 0, 0),
                seasonal_order=(1, 0, 0, 12),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False, maxiter=200)
            predicted = refit.get_forecast(steps=len(test)).predicted_mean.values
            rmse, mae, mape = _metrics(test.to_numpy(), predicted)
        else:
            rmse = mae = mape = 0.0
        return {
            "forecast": pred.predicted_mean.values.tolist(),
            "ci_width": ((ci.iloc[:, 1] - ci.iloc[:, 0]) / 2).values.tolist(),
            "aic": float(fit.aic),
            "rmse": rmse,
            "mae": mae,
            "mape": mape,
        }
    except Exception:  # noqa: BLE001
        logger.debug("SARIMAX fit failed")
        return None


def _fit_es(
    series: pd.Series,
) -> dict[str, Any] | None:
    from statsmodels.tsa.holtwinters import (
        ExponentialSmoothing,
    )

    try:
        model = ExponentialSmoothing(
            series, trend="add", seasonal="add", seasonal_periods=12
        )
        fit = model.fit(optimized=True)
        steps = min(36, len(series))
        pred = fit.forecast(steps=steps)
        residuals = fit.resid.dropna()
        resid_std = float(residuals.std()) if len(residuals) > 2 else 0.0
        ci_width = [resid_std * (1 + 0.05 * h) for h in range(1, steps + 1)]
        split = int(len(series) * 0.8)
        if split > 5:
            train, test = series.iloc[:split], series.iloc[split:]
            refit = ExponentialSmoothing(
                train, trend="add", seasonal="add", seasonal_periods=12
            ).fit(optimized=True)
            predicted = refit.forecast(len(test)).values
            rmse, mae, mape = _metrics(test.to_numpy(), predicted)
        else:
            rmse = mae = mape = 0.0
        return {
            "forecast": pred.values.tolist(),
            "ci_width": ci_width,
            "aic": float(fit.aic),
            "rmse": rmse,
            "mae": mae,
            "mape": mape,
        }
    except Exception:  # noqa: BLE001
        logger.debug("ExponentialSmoothing fit failed")
        return None


def _upsert_forecasts(db: Session, records: list[dict[str, Any]]) -> None:
    """Upsert forecast rows, keyed by (district_id, crop_id, forecast_month, forecast_model)."""
    from services.etl import _upsert_table_rows

    # ponytail: _upsert_table_rows already handles dialect detection + batching;
    # the old pg_insert/SQLite-fallback try/except was reinventing the same logic.
    _upsert_table_rows(
        "forecasts",
        records,
        ["district_id", "crop_id", "forecast_month", "forecast_model"],
        db=db,
    )
    db.commit()
