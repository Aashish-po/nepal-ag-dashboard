"""
Pytest configuration and shared fixtures.

Run tests: pytest backend/tests/ --cov=backend --cov-report=term
"""

import os
import sys

import pytest

# Ensure backend directory is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --------------------------------------------------------------------------- #
# Test environment setup
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session", autouse=True)
def _setup_test_env():
    """Set test environment variables before any imports."""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["CORS_ORIGINS"] = "http://localhost:5173"
    # Don't set DATABASE_URL — tests use mock data or in-memory SQLite
    yield


# --------------------------------------------------------------------------- #
# Sample data fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture
def sample_district_data():
    return {
        "id": 1,
        "name": "Kathmandu",
        "province": "Bagmati",
        "region": "Hill",
        "latitude": 27.7172,
        "longitude": 85.3240,
        "population": 1200000,
        "area_sq_km": 899.25,
    }


@pytest.fixture
def sample_crop_data():
    return {
        "id": 1,
        "name": "Rice",
        "fao_code": "F0027",
        "category": "Cereal",
        "unit": "MT",
        "is_export_crop": False,
        "is_subsistence": True,
    }


@pytest.fixture
def sample_yield_data():
    return [
        {
            "year": 2014,
            "production_mt": 450000,
            "area_harvested_ha": 1200000,
            "yield_kg_ha": 375,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2015,
            "production_mt": 465000,
            "area_harvested_ha": 1210000,
            "yield_kg_ha": 384,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2016,
            "production_mt": 480000,
            "area_harvested_ha": 1220000,
            "yield_kg_ha": 393,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2017,
            "production_mt": 490000,
            "area_harvested_ha": 1230000,
            "yield_kg_ha": 398,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2018,
            "production_mt": 500000,
            "area_harvested_ha": 1240000,
            "yield_kg_ha": 403,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2019,
            "production_mt": 510000,
            "area_harvested_ha": 1250000,
            "yield_kg_ha": 408,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2020,
            "production_mt": 520000,
            "area_harvested_ha": 1260000,
            "yield_kg_ha": 413,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2021,
            "production_mt": 530000,
            "area_harvested_ha": 1270000,
            "yield_kg_ha": 418,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2022,
            "production_mt": 535000,
            "area_harvested_ha": 1280000,
            "yield_kg_ha": 418,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2023,
            "production_mt": 540000,
            "area_harvested_ha": 1290000,
            "yield_kg_ha": 419,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
        {
            "year": 2024,
            "production_mt": 545000,
            "area_harvested_ha": 1300000,
            "yield_kg_ha": 419,
            "data_source": "FAOSTAT",
            "data_quality": "Official",
        },
    ]


@pytest.fixture
def sample_climate_data():
    return [
        {
            "observation_date": "2024-01-01",
            "rainfall_mm": 45.2,
            "temperature_min_c": 8.5,
            "temperature_max_c": 22.3,
            "temperature_mean_c": 15.4,
            "solar_radiation_mj_m2": 12.3,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-02-01",
            "rainfall_mm": 28.1,
            "temperature_min_c": 7.2,
            "temperature_max_c": 24.1,
            "temperature_mean_c": 15.6,
            "solar_radiation_mj_m2": 14.1,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-03-01",
            "rainfall_mm": 35.0,
            "temperature_min_c": 11.5,
            "temperature_max_c": 27.8,
            "temperature_mean_c": 20.1,
            "solar_radiation_mj_m2": 18.2,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-04-01",
            "rainfall_mm": 52.3,
            "temperature_min_c": 14.2,
            "temperature_max_c": 28.9,
            "temperature_mean_c": 21.5,
            "solar_radiation_mj_m2": 19.5,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-05-01",
            "rainfall_mm": 89.0,
            "temperature_min_c": 18.5,
            "temperature_max_c": 30.1,
            "temperature_mean_c": 24.3,
            "solar_radiation_mj_m2": 20.1,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-06-01",
            "rainfall_mm": 210.0,
            "temperature_min_c": 21.3,
            "temperature_max_c": 31.5,
            "temperature_mean_c": 26.4,
            "solar_radiation_mj_m2": 14.8,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-07-01",
            "rainfall_mm": 380.0,
            "temperature_min_c": 23.1,
            "temperature_max_c": 32.8,
            "temperature_mean_c": 27.9,
            "solar_radiation_mj_m2": 11.5,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-08-01",
            "rainfall_mm": 320.0,
            "temperature_min_c": 22.5,
            "temperature_max_c": 31.2,
            "temperature_mean_c": 26.8,
            "solar_radiation_mj_m2": 12.3,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-09-01",
            "rainfall_mm": 250.0,
            "temperature_min_c": 19.8,
            "temperature_max_c": 29.5,
            "temperature_mean_c": 24.6,
            "solar_radiation_mj_m2": 14.8,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-10-01",
            "rainfall_mm": 80.0,
            "temperature_min_c": 14.2,
            "temperature_max_c": 26.8,
            "temperature_mean_c": 20.5,
            "solar_radiation_mj_m2": 17.1,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-11-01",
            "rainfall_mm": 35.0,
            "temperature_min_c": 8.9,
            "temperature_max_c": 21.5,
            "temperature_mean_c": 15.2,
            "solar_radiation_mj_m2": 15.2,
            "data_source": "NASA POWER",
        },
        {
            "observation_date": "2024-12-01",
            "rainfall_mm": 28.0,
            "temperature_min_c": 6.5,
            "temperature_max_c": 18.9,
            "temperature_mean_c": 12.7,
            "solar_radiation_mj_m2": 12.8,
            "data_source": "NASA POWER",
        },
    ]


@pytest.fixture
def sample_heatmap_data():
    return {"total_rows": 0, "rows": []}
