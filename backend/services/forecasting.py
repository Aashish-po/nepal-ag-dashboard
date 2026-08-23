"""
Time-series forecasting services using statsmodels.

Provides ARIMA and Exponential Smoothing models for yield forecasting.
Models are trained on historical yield data (2014-2024) and produce
forecasts with 95% confidence intervals.
"""

import logging
import math
import warnings
from collections.abc import Sequence
from typing import Any

import numpy as np
from statsmodels.tsa.arima.model import ARIMA  # type: ignore
from statsmodels.tsa.holtwinters import ExponentialSmoothing  # type: ignore

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Model selection
# --------------------------------------------------------------------------- #


def select_best_model(yield_values: Sequence[float], n_periods: int) -> str:
    """Compare ARIMA and Exponential Smoothing models by AIC.

    Args:
        yield_values: Historical yield values (annual).
        n_periods: Forecast horizon.

    Returns:
        Model name: "ARIMA" or "ExponentialSmoothing".
    """
    if len(yield_values) < 5:
        return "ExponentialSmoothing"  # More robust with small samples

    aic_arima = _fit_arima_aic(yield_values)
    aic_ets = _fit_ets_aic(yield_values)

    if aic_arima < aic_ets:
        return "ARIMA"
    return "ExponentialSmoothing"


def _fit_arima_aic(values: Sequence[float]) -> float:
    """Fit ARIMA and return AIC (inf for failure)."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ARIMA(values, order=(1, 1, 1))
            fitted = model.fit(method_kwargs={"warn_convergence": False})
            return float(fitted.aic)
    except (ValueError, np.linalg.LinAlgError):
        return float("inf")


def _fit_ets_aic(values: Sequence[float]) -> float:
    """Fit Exponential Smoothing and return AIC proxy."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ExponentialSmoothing(
                values,
                trend="add",
                seasonal=None,
                initialization_method="estimated",
            )
            fitted = model.fit()
            # Use SSE / 2 as AIC proxy (statsmodels ETS doesn't always provide AIC)
            sse = (
                fitted.sse
                if hasattr(fitted, "sse")
                else sum(
                    (v - fitted.fittedvalues[i]) ** 2 for i, v in enumerate(values)
                )
            )
            k = len(values)
            if len(values) > 2:
                aic_proxy = k * math.log(sse / len(values)) + 2 * 2  # 2 params
            else:
                aic_proxy = float("inf")
            return float(aic_proxy)
    except (ValueError, np.linalg.LinAlgError):
        return float("inf")


# --------------------------------------------------------------------------- #
# Forecast generators
# --------------------------------------------------------------------------- #


def forecast_arima(
    yield_values: Sequence[float],
    years: Sequence[int],
    periods: int = 12,
) -> dict:
    """Train ARIMA(p,d,q) and return monthly forecasts with confidence intervals.

    Args:
        yield_values: Annual yield values (kg/ha).
        years: Corresponding years.
        periods: Number of months to forecast.

    Returns:
        Dict with forecasts (list), model name, RMSE, MAE, MAPE.
    """
    if len(yield_values) < 3:
        return _empty_forecast("ARIMA", periods)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Use ARIMA(1,1,1) for stability
            model = ARIMA(yield_values, order=(1, 1, 1))
            fitted = model.fit(method_kwargs={"warn_convergence": False})

            # Forecast (interpolate to monthly)
            annual_forecast = fitted.forecast(steps=max(1, periods // 12 + 1))

            # Build monthly forecasts by interpolating annual values
            forecasts = _interpolate_monthly(annual_forecast, periods)

            # Confidence intervals
            forecast_result = fitted.get_forecast(steps=max(1, periods // 12 + 1))
            ci = forecast_result.conf_int(alpha=0.05)
            if hasattr(ci, "iloc"):
                lower_annual = ci.iloc[:, 0].tolist()
                upper_annual = ci.iloc[:, 1].tolist()
            else:
                lower_annual = ci[:, 0].tolist()
                upper_annual = ci[:, 1].tolist()
            lower_monthly = _interpolate_monthly(lower_annual, periods)
            upper_monthly = _interpolate_monthly(upper_annual, periods)

            # Historical RMSE
            burn_in = 2  # d=1 plus p=1 for ARIMA(1,1,1)
            fitted_vals = fitted.fittedvalues.tolist()[burn_in:]
            actual_vals = yield_values[-len(fitted_vals) :]
            rmse, mae, mape = _compute_metrics(actual_vals, fitted_vals)

            return {
                "model": "ARIMA",
                "forecasts": forecasts,
                "lower_ci": lower_monthly,
                "upper_ci": upper_monthly,
                "rmse": rmse,
                "mae": mae,
                "mape": mape,
            }
    except (ValueError, np.linalg.LinAlgError):
        logger.warning("ARIMA forecast failed")
        return _empty_forecast("ARIMA", periods)


def forecast_exp_smoothing(
    yield_values: Sequence[float],
    years: Sequence[int],
    periods: int = 12,
) -> dict:
    """Train Exponential Smoothing and return forecasts with confidence intervals.

    Args:
        yield_values: Annual yield values.
        years: Corresponding years.
        periods: Number of months to forecast.

    Returns:
        Dict with forecasts (list), model name, RMSE, MAE, MAPE.
    """
    if len(yield_values) < 2:
        return _empty_forecast("ExponentialSmoothing", periods)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ExponentialSmoothing(
                yield_values,
                trend="add",
                seasonal=None,
                initialization_method="estimated",
            )
            fitted = model.fit()

            annual_forecast = fitted.forecast(steps=max(1, periods // 12 + 1))
            forecasts = _interpolate_monthly(annual_forecast, periods)

            # Use residual std for CI approximation
            residuals = [v - fv for v, fv in zip(yield_values, fitted.fittedvalues)]
            std_resid = np.std(residuals) if residuals else 0
            lower_monthly = [f - 1.96 * std_resid for f in forecasts]
            upper_monthly = [f + 1.96 * std_resid for f in forecasts]

            fitted_vals = fitted.fittedvalues.tolist()
            actual_vals = yield_values[-len(fitted_vals) :]
            rmse, mae, mape = _compute_metrics(actual_vals, fitted_vals)

            return {
                "model": "ExponentialSmoothing",
                "forecasts": forecasts,
                "lower_ci": lower_monthly,
                "upper_ci": upper_monthly,
                "rmse": rmse,
                "mae": mae,
                "mape": mape,
            }
    except (ValueError, np.linalg.LinAlgError):
        logger.warning("Exponential Smoothing forecast failed")
        return _empty_forecast("ExponentialSmoothing", periods)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def train_forecast(
    yield_values: Sequence[float],
    years: Sequence[int],
    months_ahead: int = 12,
) -> dict:
    """Train the best model and return forecasts.

    Args:
        yield_values: Historical annual yield values (kg/ha).
        years: Corresponding years.
        months_ahead: Forecast horizon in months (12, 24, or 36).

    Returns:
        Dict with model, forecasts, lower_ci, upper_ci, RMSE, MAE, MAPE.
    """
    if len(yield_values) < 5:
        # Not enough data — use simple moving average
        avg = sum(yield_values) / len(yield_values) if yield_values else 0
        n_months = months_ahead
        # Compute in-sample errors for the moving average
        if yield_values:
            residuals = [v - avg for v in yield_values]
            rmse = round(math.sqrt(sum(r**2 for r in residuals) / len(residuals)), 2)
            mae = round(sum(abs(r) for r in residuals) / len(residuals), 2)
            pct_errors = [
                abs(r / v) * 100 for r, v in zip(residuals, yield_values) if v != 0
            ]
            mape = round(sum(pct_errors) / len(pct_errors), 2) if pct_errors else 0.0
        else:
            rmse = None
            mae = None
            mape = None
        return {
            "model": "MovingAverage",
            "forecasts": [round(avg, 2)] * n_months,
            "lower_ci": [round(avg - avg * 0.15, 2)] * n_months,
            "upper_ci": [round(avg + avg * 0.15, 2)] * n_months,
            "rmse": rmse,
            "mae": mae,
            "mape": mape,
        }

    model_name = select_best_model(yield_values, months_ahead)

    if model_name == "ARIMA":
        result = forecast_arima(yield_values, years, months_ahead)
    else:
        result = forecast_exp_smoothing(yield_values, years, months_ahead)

    return result


def _interpolate_monthly(annual_values: Sequence[Any], n_months: int) -> list[float]:
    """Linearly interpolate annual forecast values into monthly values."""
    if len(annual_values) < 2:
        return [round(float(annual_values[0]) if annual_values else 0.0, 2)] * n_months

    monthly = []
    for month_idx in range(n_months):
        year_idx = month_idx / 12
        lower = int(year_idx)
        upper = min(lower + 1, len(annual_values) - 1)
        frac = year_idx - lower
        val = annual_values[lower] * (1 - frac) + annual_values[upper] * frac
        monthly.append(round(float(val), 2))
    return monthly


def _compute_metrics(
    actual: Sequence[float], predicted: Sequence[float]
) -> tuple[float, float, float]:
    """Compute RMSE, MAE, and MAPE."""
    if not actual or not predicted:
        return 0.0, 0.0, 0.0

    n = min(len(actual), len(predicted))
    actual = actual[-n:]
    predicted = predicted[-n:]

    squared_errors = [(a - p) ** 2 for a, p in zip(actual, predicted)]
    abs_errors = [abs(a - p) for a, p in zip(actual, predicted)]
    pct_errors = [
        abs((a - p) / a) * 100 if a != 0 else 0 for a, p in zip(actual, predicted)
    ]

    rmse = math.sqrt(sum(squared_errors) / n)
    mae = sum(abs_errors) / n
    mape = sum(pct_errors) / n

    return round(rmse, 2), round(mae, 2), round(mape, 2)


def _empty_forecast(model: str, n_months: int) -> dict:
    """Return an empty forecast result."""
    return {
        "model": model,
        "forecasts": [],
        "lower_ci": [],
        "upper_ci": [],
        "rmse": 0.0,
        "mae": 0.0,
        "mape": 0.0,
    }
