"""
Climate data processing services.

Computes climate summaries (annual rainfall, avg temperature, monsoon)
from monthly climate records.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date

logger = logging.getLogger(__name__)


def compute_climate_summary(records: list[dict]) -> dict:
    """Compute climate summary statistics from monthly records.

    Args:
        records: List of climate record dicts with rainfall_mm, temperature_mean_c,
                 observation_date fields.

    Returns:
        Dict with annual_rainfall_mm, avg_temperature_c, monsoon period.
    """
    if not records:
        return {
            "annual_rainfall_mm": None,
            "avg_temperature_c": None,
            "monsoon_start_month": 6,
            "monsoon_end_month": 9,
        }

    annual_rain: defaultdict[int, float] = defaultdict(float)
    monthly_temps: list[float] = []
    month_rainfall: defaultdict[int, float] = defaultdict(float)
    month_counts: defaultdict[int, int] = defaultdict(int)

    for rec in records:
        obs_date = rec.get("observation_date")
        if obs_date is None:
            continue

        if hasattr(obs_date, "year") and hasattr(obs_date, "month"):
            year = obs_date.year
            month = obs_date.month
        else:
            # Accept ISO strings such as "2024-01-01".
            try:
                parsed = date.fromisoformat(str(obs_date)[:10])
            except ValueError:
                logger.warning("Skipping record with unparsable date: %s", obs_date)
                continue
            year = parsed.year
            month = parsed.month

        if rec.get("rainfall_mm") is not None:
            annual_rain[year] += float(rec["rainfall_mm"])
            month_rainfall[month] += float(rec["rainfall_mm"])
            month_counts[month] += 1

        if rec.get("temperature_mean_c") is not None:
            monthly_temps.append(float(rec["temperature_mean_c"]))

    latest_year = max(annual_rain.keys()) if annual_rain else None
    avg_temp = sum(monthly_temps) / len(monthly_temps) if monthly_temps else None

    # Find monsoon period (3 consecutive months with highest total rainfall)
    month_avg = {m: month_rainfall[m] / max(month_counts[m], 1) for m in month_rainfall}

    best_sum = 0.0
    best_start = 6
    for start in range(1, 13):
        window = [((start - 1 + offset) % 12) + 1 for offset in range(3)]
        window_sum = sum(month_avg.get(m, 0) for m in window)
        if window_sum > best_sum:
            best_sum = window_sum
            best_start = start

    monsoon_start = best_start
    monsoon_end = ((best_start - 1 + 2) % 12) + 1

    return {
        "annual_rainfall_mm": (
            round(annual_rain.get(latest_year, 0), 2) if latest_year else None
        ),
        "avg_temperature_c": round(avg_temp, 2) if avg_temp is not None else None,
        "monsoon_start_month": monsoon_start,
        "monsoon_end_month": monsoon_end,
    }
