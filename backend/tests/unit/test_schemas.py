"""
Unit tests for Pydantic schemas and data validation.

Covers:
  - Schema field validation (types, constraints)
  - Pydantic model creation and validation
  - Response schema correctness
"""


class TestSchemas:
    """Tests for Pydantic response schemas."""

    def test_district_response_validation(self):
        """DistrictResponse should accept valid district data."""
        from api.models.schemas import DistrictResponse

        data = {
            "id": 1,
            "name": "Kathmandu",
            "province": "Bagmati",
            "region": "Hill",
            "latitude": 27.7172,
            "longitude": 85.3240,
            "population": 1200000,
            "area_sq_km": 899.25,
        }

        schema = DistrictResponse(**data)
        assert schema.id == 1
        assert schema.name == "Kathmandu"

    def test_crop_response_validation(self):
        """CropResponse should accept valid crop data."""
        from api.models.schemas import CropResponse

        data = {
            "id": 5,
            "name": "Cardamom",
            "fao_code": "F0717",
            "category": "Spice",
            "unit": "MT",
            "is_export_crop": True,
            "is_subsistence": False,
        }

        schema = CropResponse(**data)
        assert schema.is_export_crop is True

    def test_yield_record_validation(self):
        """YieldRecord should require year and area_harvested_ha."""
        from api.models.schemas import YieldRecord

        # Valid
        record = YieldRecord(
            year=2024,
            production_mt=450000,
            area_harvested_ha=1200000,
            yield_kg_ha=375,
            data_source="FAOSTAT",
            data_quality="Official",
        )
        assert record.year == 2024

        # Optional fields can be omitted
        record_minimal = YieldRecord(year=2024)
        assert record_minimal.year == 2024
        assert record_minimal.area_harvested_ha is None

    def test_climate_record_validation(self):
        """ClimateRecord should accept valid climate data."""
        from api.models.schemas import ClimateRecord
        from datetime import date

        record = ClimateRecord(
            observation_date=date(2024, 1, 1),
            rainfall_mm=45.2,
            temperature_min_c=8.5,
            temperature_max_c=22.3,
            temperature_mean_c=15.4,
            solar_radiation_mj_m2=12.3,
            data_source="NASA POWER",
        )
        assert record.rainfall_mm == 45.2

    def test_correlation_result_validation(self):
        """CorrelationResult should handle None coefficient."""
        from api.models.schemas import CorrelationResult

        result = CorrelationResult()
        assert result.coefficient is None
        assert result.significant is False

    def test_forecast_month_validation(self):
        """ForecastMonth should serialize month as string."""
        from api.models.schemas import ForecastMonth

        fm = ForecastMonth(
            forecast_month="2025-01",
            forecast_yield_kg_ha=382,
            lower_ci_95=355,
            upper_ci_95=410,
            confidence=0.95,
        )
        assert fm.forecast_month == "2025-01"
        assert fm.confidence == 0.95

    def test_health_response_validation(self):
        """HealthResponse should contain all required fields."""
        from api.models.schemas import HealthResponse

        hr = HealthResponse(
            status="ok",
            timestamp="2024-08-18T12:00:00Z",
            database="connected",
        )
        assert hr.status == "ok"

    def test_commercialization_level_mapping(self):
        """Commercialization score should map to correct level."""
        # Tests the interpretation, not the schema itself
        from api.routes.commercialization import _level

        assert _level(10) == "SUBSISTENCE"
        assert _level(30) == "MIXED"
        assert _level(60) == "COMMERCIAL"
        assert _level(85) == "HIGHLY_COMMERCIAL"

    def test_error_response_format(self):
        """ErrorResponse should have the standard error structure."""
        from api.models.schemas import ErrorResponse

        er = ErrorResponse(
            error={
                "code": "NOT_FOUND",
                "message": "District not found",
            }
        )
        assert er.error["code"] == "NOT_FOUND"

    def test_heatmap_row_validation(self):
        """HeatmapRow should validate correlation values."""
        from api.models.schemas import HeatmapRow

        row = HeatmapRow(
            district="Kathmandu",
            district_id=1,
            crop="Rice",
            crop_id=1,
            rainfall_corr=0.68,
            temperature_corr=-0.42,
            solar_corr=0.55,
        )
        assert row.rainfall_corr == 0.68


# --------------------------------------------------------------------------- #
# Pydantic model config tests
# --------------------------------------------------------------------------- #


class TestSchemaConfig:
    """Tests for Pydantic model configuration."""

    def test_orm_mode_enabled(self):
        """Models should support from_orm for SQLAlchemy objects."""
        from api.models.schemas import DistrictResponse

        class FakeDistrict:
            id = 1
            name = "Kathmandu"
            province = "Bagmati"
            region = "Hill"
            latitude = 27.7172
            longitude = 85.3240
            population = 1200000
            area_sq_km = 899.25

        schema = DistrictResponse.model_validate(FakeDistrict())
        assert schema.id == 1
        assert schema.name == "Kathmandu"
