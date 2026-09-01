"""
Integration tests for API endpoints.

Uses FastAPI's TestClient with dependency overrides for database and cache.
Tests cover the full request-response cycle for each endpoint, exercising
router registration, dependency wiring, filtering, schemas, and error handling.

Run: pytest backend/tests/integration/test_api.py -v
"""

from datetime import date
from typing import Any
from unittest.mock import MagicMock

import pytest
from api.db import get_db
from api.models.db_models import (
    CommercializationIndex,
    Crops,
    Districts,
    Yields,
)
from fastapi.testclient import TestClient
from main import app
from services.validators import FilterValidator, get_filter_validator

# Pre-built test fixtures for db.get()
LOOKUP = {
    (Districts, 1): Districts(
        id=1,
        name="Kathmandu",
        province="Bagmati",
        region="Hill",
        latitude=27.7172,
        longitude=85.3240,
        population=1200000,
        area_sq_km=899.25,
    ),
    (Districts, 2): Districts(
        id=2,
        name="Bhaktapur",
        province="Bagmati",
        region="Hill",
        latitude=27.6519,
        longitude=85.3897,
        population=266000,
        area_sq_km=119.36,
    ),
    (Districts, 3): Districts(
        id=3,
        name="Dhanusa",
        province="Madhesh",
        region="Terai",
        latitude=26.7289,
        longitude=85.9177,
        population=693000,
        area_sq_km=2430.49,
    ),
    (Crops, 1): Crops(
        id=1,
        name="Rice",
        fao_code="F0027",
        category="Cereal",
        is_export_crop=False,
        is_subsistence=True,
    ),
    (Crops, 5): Crops(
        id=5,
        name="Cardamom",
        fao_code="F0717",
        category="Spice",
        is_export_crop=True,
        is_subsistence=False,
    ),
}

# --------------------------------------------------------------------------- #
# Mock data constants for table queries
# --------------------------------------------------------------------------- #

_TEST_DISTRICTS = [
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
    Districts(
        id=3,
        name="Dhanusa",
        province="Madhesh",
        region="Terai",
        latitude=26.7289,
        longitude=85.9177,
        population=693000,
        area_sq_km=2430.49,
    ),
]

_TEST_CROPS = [
    Crops(
        id=1,
        name="Rice",
        fao_code="F0027",
        category="Cereal",
        unit="MT",
        is_export_crop=False,
        is_subsistence=True,
    ),
    Crops(
        id=5,
        name="Cardamom",
        fao_code="F0717",
        category="Spice",
        unit="MT",
        is_export_crop=True,
        is_subsistence=False,
    ),
]

_TEST_YIELDS = [
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
    Yields(
        id=3,
        district_id=1,
        crop_id=1,
        year=2022,
        production_mt=430000,
        area_harvested_ha=1180000,
        yield_kg_ha=365.0,
        data_source="FAOSTAT",
        data_quality="Official",
    ),
]

_TEST_CLIMATE_ROWS = [
    (date(2024, 1, 15), 20.5, 8.0, 18.0, 12.0, 12.5, "NASA POWER"),
    (date(2024, 7, 15), 85.0, 22.0, 35.0, 28.0, 22.0, "NASA POWER"),
    (date(2023, 1, 15), 15.0, 6.0, 15.0, 10.0, 10.0, "NASA POWER"),
    (date(2023, 7, 15), 70.0, 20.0, 32.0, 26.0, 20.0, "NASA POWER"),
    (date(2022, 1, 15), 12.0, 4.0, 13.0, 8.0, 8.0, "NASA POWER"),
    (date(2022, 7, 15), 60.0, 18.0, 30.0, 24.0, 18.0, "NASA POWER"),
]

_TEST_COMMERIALIZATION = [
    CommercializationIndex(
        id=1,
        district_id=1,
        year=2024,
        export_crop_area_pct=35.0,
        subsistence_area_pct=40.0,
        avg_holding_size_ha=0.8,
        export_volume_ratio=1.2,
        commercialization_score=42.5,
    ),
]

_TEST_FORECASTS = [
    (date(2024, 1, 1), 380.0, 350.0, 410.0, "ARIMA", 15.0, 10.0, 2.5),
    (date(2024, 2, 1), 385.0, 355.0, 415.0, "ARIMA", 14.0, 9.0, 2.3),
]


def mock_get(*args, **kwargs):
    """Mock implementation for db.get()."""
    entity = args[0] if len(args) >= 1 else kwargs.get("entity")
    pk = args[1] if len(args) >= 2 else kwargs.get("pk")
    if isinstance(entity, type) and (entity, pk) in LOOKUP:
        return LOOKUP[(entity, pk)]
    return None


def create_mock_execute(result_rows, return_type="scalars"):
    """Create a mock result object for session.execute()."""
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
    """Extract table name from a SQLAlchemy statement."""
    # Try to get table name from stmt.table
    table = getattr(stmt, "table", None)
    if table is not None:
        name = getattr(table, "name", None)
        if isinstance(name, str):
            return name

    # Handle JOIN queries: scan all FROM clauses for table names
    try:
        from_list = getattr(stmt, "get_final_froms", None)
        if from_list is not None:
            for f in from_list():
                n = getattr(f, "name", None)
                if isinstance(n, str):
                    return n
    except Exception:  # noqa: BLE001,S110 — stub DB layer must swallow any SQLAlchemy introspection failure
        pass

    # Try to get table name from selected_columns
    try:
        for col in stmt.selected_columns:
            # Try to get table from column directly
            t = getattr(col, "table", None)
            if t is not None:
                n = getattr(t, "name", None)
                if isinstance(n, str):
                    return n
            # Try to unwrap common column wrappers to find table
            for attr in ("expression", "column", "expr", "_expression", "_column"):
                wrapped = getattr(col, attr, None)
                if wrapped is not None:
                    t = getattr(wrapped, "table", None)
                    if t is not None:
                        n = getattr(t, "name", None)
                        if isinstance(n, str):
                            return n
    except AttributeError:
        pass

    # Try to get table name from _raw_columns
    try:
        for col in getattr(stmt, "_raw_columns", []):
            # Try to get table from column directly
            t = getattr(col, "table", None)
            if t is not None:
                n = getattr(t, "name", None)
                if isinstance(n, str):
                    return n
            # Try to unwrap common column wrappers to find table
            for attr in ("expression", "column", "expr", "_expression", "_column"):
                wrapped = getattr(col, attr, None)
                if wrapped is not None:
                    t = getattr(wrapped, "table", None)
                    if t is not None:
                        n = getattr(t, "name", None)
                        if isinstance(n, str):
                            return n
    except AttributeError:
        pass

    # Detect raw SQL queries by string content
    stmt_str = str(stmt).lower()
    if "from climate" in stmt_str or "climate" in stmt_str.split("where")[0]:
        return "climate"
    if "from forecasts" in stmt_str or "forecasts" in stmt_str.split("where")[0]:
        return "forecasts"
    if "from commercialization" in stmt_str:
        return "commercialization_index"

    return None


def apply_where(stmt, rows):
    """Filter rows based on WHERE clause in the select statement."""
    where = getattr(stmt, "whereclause", None)
    if where is None:
        return rows

    from sqlalchemy.sql.elements import BindParameter

    clause_list = getattr(where, "clauses", [where])

    for condition in clause_list:
        col = getattr(condition, "left", None)
        col_name = getattr(col, "key", None)
        if col_name is None:
            continue

        right = getattr(condition, "right", None)
        if right is None:
            continue

        # Use BindParameter.value for literal API filters
        if isinstance(right, BindParameter):
            right = right.value

        # Safely unwrap SQLAlchemy values
        if right is not None:
            right = getattr(right, "_value", right)

        op = getattr(condition, "operator", None)
        op_name = getattr(op, "__name__", "")

        rows = _apply_op(rows, col_name, op_name, right)

    return rows


def _apply_op(rows, col_name, op_name, value):
    """Apply a comparison operator to filter rows."""
    import operator as op_mod

    ops = {
        "eq": op_mod.eq,
        "ne": op_mod.ne,
        "ge": op_mod.ge,
        "le": op_mod.le,
        "gt": op_mod.gt,
        "lt": op_mod.lt,
        "is": lambda x, y: x is y,
        "is_not": lambda x, y: x is not y,
        "is_not_": lambda x, y: (
            x is not y
        ),  # ponytail: handles .isnot() operator name alias
        "is_": lambda x, y: x is y,  # ponytail: handles .is_(value) operator name alias
        "isnot": lambda x, y: (
            x is not y
        ),  # ponytail: handles .isnot(None) operator name
    }
    func = ops.get(op_name)
    if func is None:
        raise ValueError(f"Unsupported operator: {op_name}")
    try:
        return [r for r in rows if func(getattr(r, col_name, None), value)]
    except (AttributeError, TypeError) as e:
        raise ValueError(f"Comparison error for {col_name} {op_name} {value}: {e}")


def mock_execute_side_effect(stmt):
    """Side effect for session.execute() that returns appropriate mock data."""
    table_name = get_table_name(stmt)

    # Handle raw SQL (text queries) — detect by absence of .table and presence of FROM clause
    if table_name is None:
        stmt_str = str(stmt).lower()
        if "from climate" in stmt_str or "climate" in stmt_str:
            return create_mock_execute(_TEST_CLIMATE_ROWS, return_type="fetchall")
        # Other text queries without recognizable table — fall through

    # Handle district queries
    if table_name == "districts":
        selected_columns = getattr(stmt, "selected_columns", None)

        if selected_columns is not None and len(selected_columns) == 1:
            col = selected_columns[0]
            col_str = str(col).lower()
            if "province" in col_str:
                return create_mock_execute(
                    ["Bagmati", "Madhesh"], return_type="scalars"
                )
            if "distinct" in col_str and "province" in col_str:
                return create_mock_execute(
                    ["Bagmati", "Madhesh"], return_type="scalars"
                )
            if "region" in col_str:
                return create_mock_execute(["Hill", "Terai"], return_type="scalars")
            if "distinct" in col_str and "region" in col_str:
                return create_mock_execute(["Hill", "Terai"], return_type="scalars")
            if "id" in col_str and "district" in col_str:
                filtered = apply_where(stmt, _TEST_DISTRICTS)
                return create_mock_execute(
                    [d.id for d in filtered], return_type="scalars"
                )

        return create_mock_execute(apply_where(stmt, _TEST_DISTRICTS))

    # Handle crop queries
    if table_name == "crops":
        selected_columns = getattr(stmt, "selected_columns", None)

        if selected_columns is not None and len(selected_columns) == 1:
            col = selected_columns[0]
            col_str = str(col).lower()
            if "id" in col_str:
                filtered = apply_where(stmt, _TEST_CROPS)
                return create_mock_execute(
                    [c.id for c in filtered], return_type="scalars"
                )

        return create_mock_execute(apply_where(stmt, _TEST_CROPS))

    # Handle yield queries
    if table_name == "yields":
        return create_mock_execute(apply_where(stmt, _TEST_YIELDS))

    # Handle commercialization_index queries
    if table_name == "commercialization_index":
        return create_mock_execute(apply_where(stmt, _TEST_COMMERIALIZATION))

    # Handle forecasts queries
    if table_name == "forecasts":
        return create_mock_execute(_TEST_FORECASTS, return_type="all")

    # Handle raw SQL text queries (used by correlations service)
    stmt_str = str(stmt).lower()
    if "climate" in stmt_str and "district_id" in stmt_str:
        return create_mock_execute(_TEST_CLIMATE_ROWS, return_type="fetchall")
    if "forecasts" in stmt_str and ("district_id" in stmt_str or "crop_id" in stmt_str):
        return create_mock_execute(_TEST_FORECASTS, return_type="all")

    # Default empty result
    return create_mock_execute([])


# --------------------------------------------------------------------------- #
# Pytest fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture
def client():
    """Create a TestClient for the production application with dependency overrides."""
    # Mock database session
    mock_session = MagicMock()

    mock_session.get = mock_get

    def execute_side_effect(*args, **kwargs):
        stmt = args[0] if args else kwargs.get("statement")
        return mock_execute_side_effect(stmt)

    mock_session.execute = execute_side_effect

    # Override dependencies - get_db must return the session directly so routes
    # receive a usable object (not a generator). get_filter_validator wraps the
    # same session in a FilterValidator.
    app.dependency_overrides[get_db] = lambda: mock_session
    app.dependency_overrides[get_filter_validator] = lambda: FilterValidator(
        mock_session
    )

    # Mock database connection check for health endpoint
    import main

    original_check = main.check_db_connection
    main.check_db_connection = lambda: "connected"

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    main.check_db_connection = original_check


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


# --------------------------------------------------------------------------- #
# Test classes
# --------------------------------------------------------------------------- #


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
        # Should return only Kathmandu and Bhaktapur (both Bagmati)
        assert len(data["districts"]) == 2
        district_ids = [d["id"] for d in data["districts"]]
        assert set(district_ids) == {1, 2}
        assert all(d["province"] == "Bagmati" for d in data["districts"])

    def test_filter_by_region(self, client):
        response = client.get("/api/v1/districts?region=Hill")
        assert response.status_code == 200
        data = response.json()
        # Should return only Kathmandu and Bhaktapur (both Hill region)
        assert len(data["districts"]) == 2
        district_ids = [d["id"] for d in data["districts"]]
        assert set(district_ids) == {1, 2}
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
        assert data["district_id"] == 1
        assert "timeseries" in data
        assert "statistics" in data
        assert isinstance(data["timeseries"], list)

    def test_yields_year_filter(self, client):
        """year_start and year_end should filter results."""
        # Test data has years 2023, 2024; request range 2024-2024
        response = client.get("/api/v1/yields/1/1?year_start=2024&year_end=2024")
        assert response.status_code == 200
        data = response.json()
        for ts in data["timeseries"]:
            assert ts["year"] == 2024
        # Should return only the 2024 record
        assert len(data["timeseries"]) == 1
        assert data["timeseries"][0]["year"] == 2024

    def test_yields_nonexistent_district(self, client):
        """Non-existent district should return 404."""
        response = client.get("/api/v1/yields/999/1")
        assert response.status_code == 404


class TestClimateEndpoint:
    """Tests for GET /api/v1/climate/{district_id}."""

    def test_climate_response_structure(self, client):
        """Response should have data array and summary."""
        response = client.get("/api/v1/climate/1")
        assert response.status_code == 200
        data = response.json()
        assert data["district_id"] == 1
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_climate_data_fields(self, client):
        """Climate data should have required fields."""
        response = client.get("/api/v1/climate/1")
        assert response.status_code == 200
        data = response.json()
        if data["data"]:
            record = data["data"][0]
            assert "observation_date" in record
            assert "rainfall_mm" in record
            assert "temperature_mean_c" in record


class TestCorrelationEndpoint:
    """Tests for GET /api/v1/correlation/{district_id}."""

    def test_correlation_response_structure(self, client):
        """Response should have correlations and R-squared."""
        response = client.get("/api/v1/correlation/1?crop_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "correlations" in data
        assert "r_squared" in data


class TestExportCropsEndpoint:
    """Tests for GET /api/v1/export-crops/{district_id}."""

    def test_export_crops_response_structure(self, client):
        """Response should have export crops data."""
        response = client.get("/api/v1/export-crops/1?year=2024")
        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2024
        assert "export_crops" in data


class TestCommercializationEndpoint:
    """Tests for GET /api/v1/commercialization."""

    def test_commercialization_response_structure(self, client):
        """Response should have commercialization score."""
        response = client.get("/api/v1/commercialization/1?year=2024")
        assert response.status_code == 200
        data = response.json()
        assert "commercialization_score" in data
        assert data["district_id"] == 1

    def test_commercialization_list_endpoint(self, client):
        """List endpoint should return ranked districts."""
        response = client.get("/api/v1/commercialization?year=2024")
        assert response.status_code == 200
        data = response.json()
        assert "year" in data
        assert "districts" in data


class TestExportsEndpoint:
    """Tests for export endpoints."""

    def test_export_yields_csv(self, client):
        """CSV export should return proper content type."""
        response = client.get(
            "/api/v1/export/yields?district_id=1&crop_id=1&format=csv"
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    def test_export_forecasts_excel(self, client):
        """Excel export should return workbook."""
        response = client.get(
            "/api/v1/export/forecasts?district_id=1&crop_id=1&format=excel"
        )
        assert response.status_code == 200
        # Verify content-disposition header for download
        assert "attachment" in response.headers.get("content-disposition", "")


class TestErrorHandling:
    """Tests for error handling across endpoints."""

    def test_invalid_year_returns_422(self, client):
        """Invalid year parameters should return 422 (FastAPI validation)."""
        response = client.get("/api/v1/yields/1/1?year_start=2000&year_end=2024")
        assert response.status_code == 422
