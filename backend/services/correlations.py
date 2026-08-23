"""
Correlation analysis services.

Provides:
  - Pearson correlation with p-values and significance
  - Lagged correlation detection
  - Yield statistics computation (trend, CAGR, volatility)
  - Cross-correlation between yield and climate variables
"""

from __future__ import annotations

import logging
import math
from collections import defaultdict
from collections.abc import Sequence
from typing import Any, Protocol, cast

from scipy import stats  # type: ignore[import-untyped]
from sqlalchemy import text

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Yield statistics
# --------------------------------------------------------------------------- #


class YieldLike(Protocol):
    """Structural type for rows with yield stats fields."""

    year: Any
    yield_kg_ha: Any


def calculate_yield_statistics(yield_rows: Sequence[YieldLike]) -> dict[str, Any]:
    """Compute trend, CAGR, volatility from historical yield records.

    Args:
        yield_rows: List of ORM Yield objects with ``year`` and ``yield_kg_ha`` attributes.

    Returns:
        Dict with avg_yield_kg_ha, max/min, volatility (std dev), cagr_pct, trend.
    """
    valid = [r for r in yield_rows if r.yield_kg_ha is not None]
    if not valid:
        return {
            "avg_yield_kg_ha": None,
            "max_yield_kg_ha": None,
            "min_yield_kg_ha": None,
            "volatility": None,
            "cagr_pct": None,
            "trend": "INSUFFICIENT_DATA",
        }

    # Sort valid rows by year, then derive both lists from the sorted sequence
    sorted_valid = sorted(valid, key=lambda r: int(r.year))
    years = [int(r.year) for r in sorted_valid]
    values = [float(r.yield_kg_ha or 0) for r in sorted_valid]
    n = len(values)

    if n < 2:
        return {
            "avg_yield_kg_ha": values[0] if values else None,
            "max_yield_kg_ha": values[0] if values else None,
            "min_yield_kg_ha": values[0] if values else None,
            "volatility": 0.0,
            "cagr_pct": None,
            "trend": "INSUFFICIENT_DATA",
        }

    avg_yield = sum(values) / n
    max_yield = max(values)
    min_yield = min(values)
    volatility = (
        math.sqrt(sum((v - avg_yield) ** 2 for v in values) / n) if n > 1 else 0.0
    )

    # CAGR calculation
    first_val = values[0]
    last_val = values[-1]
    n_years = years[-1] - years[0]
    cagr = None
    if n_years > 0 and first_val > 0:
        cagr = ((last_val / first_val) ** (1 / n_years) - 1) * 100

    # Trend detection (linear regression slope)
    trend = "STABLE"
    if n >= 3:
        try:
            result = stats.linregress(years, values)
            slope = float(cast(Any, result).slope)

            # Slope threshold: 0.5 kg/ha per year
            if slope > 0.5:
                trend = "INCREASING"
            elif slope < -0.5:
                trend = "DECREASING"
            else:
                trend = "STABLE"
        except ValueError:
            pass

    return {
        "avg_yield_kg_ha": round(avg_yield, 2),
        "max_yield_kg_ha": round(max_yield, 2),
        "min_yield_kg_ha": round(min_yield, 2),
        "volatility": round(volatility, 2),
        "cagr_pct": round(cagr, 2) if cagr is not None else None,
        "trend": trend,
    }


# --------------------------------------------------------------------------- #
# Pearson correlation
# --------------------------------------------------------------------------- #


def compute_pearson(
    x: Sequence[float | None], y: Sequence[float | None]
) -> float | None:
    """Compute Pearson correlation coefficient.

    Args:
        x: First variable values.
        y: Second variable values.

    Returns:
        Correlation coefficient (-1 to +1), or None if insufficient data.
    """
    if len(x) < 3 or len(x) != len(y):
        return None

    # Filter out None/NaN values pairwise
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return None

    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]

    corr_raw, p_value_raw = cast(tuple[float, float], stats.pearsonr(xs, ys))
    corr = float(corr_raw)
    p_value = float(p_value_raw)

    if math.isnan(corr) or math.isnan(p_value):
        return None

    return float(corr)


def compute_full_correlation(
    x: Sequence[float | None], y: Sequence[float | None]
) -> dict:
    """Compute Pearson correlation with coefficient, p-value, and significance.

    Args:
        x: First variable values (e.g., yield).
        y: Second variable values (e.g., rainfall).

    Returns:
        Dict with coefficient, p_value, significant.
    """
    if len(x) < 3 or len(x) != len(y):
        return {"coefficient": None, "p_value": None, "significant": False}

    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return {"coefficient": None, "p_value": None, "significant": False}

    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]

    corr_raw, p_value_raw = cast(tuple[float, float], stats.pearsonr(xs, ys))
    corr = float(corr_raw)
    p_value = float(p_value_raw)

    if math.isnan(corr) or math.isnan(p_value):
        return {"coefficient": None, "p_value": None, "significant": False}

    return {
        "coefficient": round(corr, 4),
        "p_value": round(p_value, 4),
        "significant": p_value < 0.05,
    }


def aggregate_annual_climate(rows: Sequence[Any]) -> dict[str, dict[int, float]]:
    """Aggregate monthly climate rows with the dashboard's shared yearly rules."""
    yearly_rain: defaultdict[int, list[float]] = defaultdict(list)
    yearly_temp: defaultdict[int, list[float]] = defaultdict(list)
    yearly_solar: defaultdict[int, list[float]] = defaultdict(list)

    for row in rows:
        observation_date = getattr(row, "observation_date", row[0])
        rainfall = getattr(row, "rainfall_mm", row[1])
        temperature = getattr(row, "temperature_mean_c", row[2])
        solar = getattr(row, "solar_radiation_mj_m2", row[3])
        year = observation_date.year
        if rainfall is not None:
            yearly_rain[year].append(float(rainfall))
        if temperature is not None:
            yearly_temp[year].append(float(temperature))
        if solar is not None:
            yearly_solar[year].append(float(solar))

    return {
        "rainfall_mm": {year: sum(values) for year, values in yearly_rain.items()},
        "temperature_mean_c": {
            year: sum(values) / len(values) for year, values in yearly_temp.items()
        },
        "solar_radiation_mj_m2": {
            year: sum(values) / len(values) for year, values in yearly_solar.items()
        },
    }


# --------------------------------------------------------------------------- #
# Yield-climate correlation (used by /api/v1/correlation endpoint)
# --------------------------------------------------------------------------- #


def compute_yield_climate_correlation(
    district_id: int,
    crop_id: int,
    yield_years: Sequence[int],
    yield_values: Sequence[float | None],
    lag_months: int = 0,
    db=None,
) -> dict | None:
    """Compute Pearson correlations between yield and climate variables.

    For each climate variable (rainfall, temperature, solar), computes:
      - Pearson correlation coefficient
      - p-value
      - R-squared (coefficient of determination)

    Args:
        district_id: District ID for climate data lookup.
        crop_id: Crop ID.
        yield_years: List of years with yield data.
        yield_values: List of yield values (kg/ha).
        lag_months: Number of months climate leads yield.
        db: Session for database queries.

    Returns:
        Dict with correlations, r_squared, interpretation.
        None if insufficient climate data.
    """
    if db is None:
        return None

    # Fetch climate data for this district
    climate_stmt = text("""
            SELECT observation_date, rainfall_mm, temperature_mean_c, solar_radiation_mj_m2
            FROM climate
            WHERE district_id = :district_id
            ORDER BY observation_date
            """)
    climate_result = db.execute(climate_stmt, {"district_id": district_id})
    climate_rows = climate_result.fetchall()

    if not climate_rows:
        return None

    annual = aggregate_annual_climate(climate_rows)
    annual_rain = annual["rainfall_mm"]
    annual_temp = annual["temperature_mean_c"]
    annual_solar = annual["solar_radiation_mj_m2"]

    # Align with yield years (apply lag if specified)
    # Lag means: climate in year Y affects yield in year Y + lag_months/12
    if lag_months > 0:
        if lag_months % 12 != 0:
            raise ValueError(f"lag_months must be a multiple of 12 (got {lag_months})")
        lag_years = lag_months // 12
    else:
        lag_years = 0

    aligned_yield = []
    aligned_rain = []
    aligned_temp = []
    aligned_solar = []

    for i, yr in enumerate(yield_years):
        val = yield_values[i]
        if val is None:
            continue

        climate_yr = yr - lag_years
        if climate_yr in annual_rain:
            aligned_yield.append(val)
            aligned_rain.append(annual_rain[climate_yr])
            aligned_temp.append(annual_temp.get(climate_yr, None))
            aligned_solar.append(annual_solar.get(climate_yr, None))

    if len(aligned_yield) < 3:
        return None

    rain_corr = compute_full_correlation(aligned_yield, aligned_rain)
    temp_corr = compute_full_correlation(aligned_yield, aligned_temp)
    solar_corr = compute_full_correlation(aligned_yield, aligned_solar)

    # Compute R-squared (use rainfall as primary predictor for R²)
    r_squared = None
    if rain_corr.get("coefficient") is not None:
        r_squared = round(rain_corr["coefficient"] ** 2, 4)

    # Interpretation
    interpretation = _generate_interpretation(rain_corr, temp_corr, solar_corr)

    return {
        "correlations": {
            "rainfall_mm": rain_corr,
            "temperature_mean_c": temp_corr,
            "solar_radiation_mj_m2": solar_corr,
        },
        "r_squared": r_squared,
        "interpretation": interpretation,
    }


def _generate_interpretation(rain_corr: dict, temp_corr: dict, solar_corr: dict) -> str:
    """Generate a human-readable interpretation of correlation results."""
    parts = []

    rain_c = rain_corr.get("coefficient")
    temp_c = temp_corr.get("coefficient")
    solar_c = solar_corr.get("coefficient")

    if rain_c is not None:
        if rain_c > 0.4:
            parts.append("Rainfall positively correlates with yield")
        elif rain_c < -0.4:
            parts.append("Rainfall negatively correlates with yield")

    if temp_c is not None:
        if temp_c > 0.4:
            parts.append("Temperature positively correlates with yield")
        elif temp_c < -0.4:
            parts.append("Temperature negatively correlates with yield")

    if solar_c is not None and solar_c > 0.3:
        parts.append("Solar radiation supports yield growth")

    if not parts:
        return "Weak correlations detected; multiple factors may influence yield."

    return "; ".join(parts) + "."
