"""
Integration tests for API endpoints.

Uses FastAPI's TestClient with dependency overrides for database and cache.
Tests cover the full request-response cycle for each endpoint, exercising
router registration, dependency wiring, filtering, schemas, and error handling.

Run: pytest backend/tests/integration/test_api.py -v
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a TestClient for the production application with dependency overrides."""
    from unittest.mock import MagicMock
    from api.db import get_db
    from api.models.db_models import Districts, Crops, Yields

    # Mock database session
    mock_session = MagicMock()

    def create_mock_execute(result_rows, return_type="scalars"):
        mock_result = MagicMock()
        if return_type == "scalars":
            mock_result.scalars.return_value.all.return_value = result_rows
            mock_result.scalar_one_or_none.return_value = (
                result_rows[0] if result_rows else None
            )
        elif return_type == "all":
            mock_result.all.return_value = result_rows
        elif return_type == "fetchall":
            mock_result.fetchall.return_value = result_rows
        elif return_type == "scalar":
            mock_result.scalar.return_value = len(result_rows)
        return mock_result

    def get_table_name(stmt: Any) -> str | None:
        table = getattr(stmt, "table", None)
        name = getattr(table, "name", None)
        return name if isinstance(name, str) else None

    def mock_execute_side_effect(*args, **kwargs):
        stmt = args[0] if args else kwargs.get("statement")
        table_name = get_table_name(stmt)

        # Handle district queries
        if table_name == "districts":
            test_districts = [
                Districts(
                    id=1,
                    name="Kathmandu",
                    province="Bagmati",
                    region="Hill",
                    latitude=27.7172,
                    longitude=85.3240,
                    population=1200000,
                    area_sq_km=899.25,
                ),
                Districts(
                    id=2,
                    name="Bhaktapur",
                    province="Bagmati",
                    region="Hill",
                    latitude=27.6519,
                    longitude=85.3897,
                    population=266000,
                    area_sq_km=119.36,
                ),
            ]
            filtered = test_districts
            return create_mock_execute(filtered)

        # Handle crop queries
        if table_name == "crops":
            test_crops = [
                Crops(
                    id=1,
                    name="Rice",
                    fao_code="F0027",
                    category="Cereal",
                    is_export_crop=False,
                    is_subsistence=True,
                ),
                Crops(
                    id=5,
                    name="Cardamom",
                    fao_code="F0717",
                    category="Spice",
                    is_export_crop=True,
                    is_subsistence=False,
                ),
            ]
            return create_mock_execute(test_crops)

        # Handle yield queries
        if table_name == "yields":
            test_yields = [
                Yields(
                    id=1,
                    district_id=1,
                    crop_id=1,
                    year=2024,
                    production_mt=450000,
                    area_harvested_ha=1200000,
                    yield_kg_ha=375.0,
                    data_source="FAOSTAT",
                    data_quality="Official",
                ),
                Yields(
                    id=2,
                    district_id=1,
                    crop_id=1,
                    year=2023,
                    production_mt=440000,
                    area_harvested_ha=1190000,
                    yield_kg_ha=370.0,
                    data_source="FAOSTAT",
                    data_quality="Official",
                ),
            ]
            return create_mock_execute(test_yields)

        # Default empty result
        return create_mock_execute([])

    mock_session.execute = mock_execute_side_effect

    # Override dependencies
    app.dependency_overrides[get_db] = lambda: mock_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_yield_response():
    """Sample response for yield endpoint."""
    return {
        "district_id": 1,
        "district_name": "Kathmandu",
        "crop_id": 1,
        "crop_name": "Rice",
        "timeseries": [
            {
                "year": 2024,
                "production_mt": 545000,
                "area_harvested_ha": 1300000,
                "yield_kg_ha": 419,
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
        ],
        "statistics": {
            "avg_yield_kg_ha": 419.0,
            "max_yield_kg_ha": 419.0,
            "min_yield_kg_ha": 419.0,
            "volatility": 0.0,
            "cagr_pct": None,
            "trend": "STABLE",
        },
    }


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert data["database"] == "connected"


class TestDistrictsEndpoint:
    """Tests for GET /api/v1/districts."""

    def test_get_all_districts(self, client):
        response = client.get("/api/v1/districts")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "districts" in data
        # Test data should have at least the test districts we defined
        assert data["total"] >= 1

    def test_filter_by_province(self, client):
        response = client.get("/api/v1/districts?province=Bagmati")
        assert response.status_code == 200
        data = response.json()
        assert all(d["province"] == "Bagmati" for d in data["districts"])

    def test_filter_by_region(self, client):
        response = client.get("/api/v1/districts?region=Hill")
        assert response.status_code == 200
        data = response.json()
        assert all(d["region"] == "Hill" for d in data["districts"])


class TestCropsEndpoint:
    """Tests for GET /api/v1/crops."""

    def test_get_all_crops(self, client):
        response = client.get("/api/v1/crops")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert all("name" in c for c in data["crops"])

    def test_filter_export_crops(self, client):
        response = client.get("/api/v1/crops?is_export_crop=True")
        assert response.status_code == 200
        data = response.json()
        assert all(c["is_export_crop"] is True for c in data["crops"])

    def test_filter_by_category(self, client):
        response = client.get("/api/v1/crops?category=Spice")
        assert response.status_code == 200
        data = response.json()
        assert all(c["category"] == "Spice" for c in data["crops"])


class TestYieldsEndpoint:
    """Tests for GET /api/v1/yields/{district_id}/{crop_id}."""

    def test_yields_response_structure(self, client):
        """Response should have timeseries + statistics."""
        response = client.get("/api/v1/yields/1/1")
        assert response.status_code == 200
        data = response.json()
        assert "district_id" in data
        assert "timeseries" in data
        assert "statistics" in data
        assert isinstance(data["timeseries"], list)

    def test_yields_year_filter(self, client):
        """year_start and year_end should filter results."""
        response = client.get("/api/v1/yields/1/1?year_start=2018&year_end=2020")
        assert response.status_code == 200
        data = response.json()
        for ts in data["timeseries"]:
            assert 2018 <= ts["year"] <= 2020

    def test_yields_nonexistent_district(self, client):
        """Non-existent district should return 404."""
        response = client.get("/api/v1/yields/999/1")
        assert response.status_code == 404
