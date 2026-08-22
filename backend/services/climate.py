"""
Climate data processing services.

Handles:
  - Fetching climate data from NASA POWER and CHIRPS APIs
  - Normalizing monthly climate records
  - Computing climate summaries (annual rainfall, avg temperature, monsoon)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date
from typing import Any, cast

import requests

logger = logging.getLogger(__name__)

CHIRPS_BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly"
NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"


def fetch_chirps_data(
    district_id: int,
    lat: float,
    lon: float,
    start_year: int = 2014,
    end_year: int = 2024,
) -> list[dict]:
    """Fetch CHIRPS rainfall data for a district centroid.

    Note: CHIRPS provides rainfall only; temperature and solar come from NASA POWER.

    Args:
        district_id: Internal district ID.
        lat: Latitude of district centroid.
        lon: Longitude of district centroid.
        start_year: Start year.
        end_year: End year.

    Returns:
        List of climate records (dicts).
    """
    records: list[dict[str, Any]] = []
    # In production, this would download actual CHIRPS data
    # For Phase 1, we rely on seed data (chirps_2014_2024.csv)
    logger.info(
        "CHIRPS data should be fetched for district %d (lat=%s, lon=%s)",
        district_id,
        lat,
        lon,
    )
    return records


def fetch_nasa_power_data(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Fetch climate data from NASA POWER API.

    Args:
        lat: Latitude of district centroid.
        lon: Longitude of district centroid.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).

    Returns:
        Dict with temperature, solar radiation, and other parameters.
    """
    params: dict[str, str | float] = {
        "parameters": "T2M_MIN,T2M_MAX,ALLSKY_SFC_SW_DWN",
        "community": "re",
        "longitude": lon,
        "latitude": lat,
        "start": start_date.replace("-", ""),
        "end": end_date.replace("-", ""),
        "format": "JSON",
    }

    try:
        response = requests.get(NASA_POWER_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            return cast(dict[str, Any], data)
        return {}
    except Exception as e:
        logger.error("NASA POWER API error: %s", e)
        return {}


def normalize_nasa_power(raw_data: dict, district_id: int) -> list[dict]:
    """Normalize NASA POWER response into database records.

    Args:
        raw_data: Raw JSON response from NASA POWER.
        district_id: Internal district ID.

    Returns:
        List of climate record dicts.
    """
    records: list[dict[str, Any]] = []
    try:
        properties = raw_data.get("properties", {})
        parameter = properties.get("parameter", {})

        t_min = parameter.get("T2M_MIN", {})
        t_max = parameter.get("T2M_MAX", {})
        solar = parameter.get("ALLSKY_SFC_SW_DWN", {})

        # NASA POWER returns a "YYYY13" annual aggregate; skip it.
        months = sorted(
            {k for k in (*t_min, *t_max, *solar) if len(k) == 6 and k[4:6] != "13"}
        )

        def measurement(values: dict, month: str) -> float | None:
            value = values.get(month)
            if value is None or float(value) == -999:
                return None
            return float(value)

        for month_str in months:
            # Month string format: YYYYMM
            year = int(month_str[:4])
            month = int(month_str[4:6])
            obs_date = date(year, month, 1)

            min_temp = measurement(t_min, month_str)
            max_temp = measurement(t_max, month_str)
            record = {
                "district_id": district_id,
                "observation_date": obs_date,
                "rainfall_mm": None,  # From CHIRPS
                "temperature_min_c": min_temp,
                "temperature_max_c": max_temp,
                "temperature_mean_c": (
                    (min_temp + max_temp) / 2
                    if min_temp is not None and max_temp is not None
                    else None
                ),
                "solar_radiation_mj_m2": measurement(solar, month_str),
                "data_source": "NASA POWER",
            }
            records.append(record)
    except Exception as e:
        logger.error("Error normalizing NASA POWER data: %s", e)

    return records


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
