"""
Pydantic response schemas for the Nepal Agricultural Intelligence Dashboard.

All models are configured with ``from_attributes=True`` so SQLAlchemy ORM
objects can be serialized directly via ``model_validate``.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator


def _serialize_decimal(v: Any) -> Any:
    """Convert Decimal to float for JSON serialization."""
    if isinstance(v, Decimal):
        return float(v)
    return v


# ---------------------------------------------------------------------------
# Shared config
# ---------------------------------------------------------------------------


class SchemaBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        protected_namespaces=(),
    )


class DecimalFloatMixin:
    @field_validator(
        "yield_kg_ha",
        "production_mt",
        "area_harvested_ha",
        "rmse_kg_ha",
        "mae_kg_ha",
        "mape_pct",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _convert_decimal(cls, v: Any) -> Any:
        if isinstance(v, Decimal):
            return float(v)
        if v is None:
            return None
        return v


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------


class DistrictResponse(SchemaBase):
    id: int
    name: str
    province: str
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None
    area_sq_km: Optional[float] = None
    created_at: Optional[str] = None


class DistrictListResponse(SchemaBase):
    total: int
    districts: list[DistrictResponse]


class CropResponse(SchemaBase):
    id: int
    name: str
    fao_code: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = "MT"
    is_export_crop: Optional[bool] = False
    is_subsistence: Optional[bool] = False
    created_at: Optional[datetime] = None


class CropListResponse(SchemaBase):
    total: int
    crops: list[CropResponse]


# ---------------------------------------------------------------------------
# Yield schemas
# ---------------------------------------------------------------------------


class YieldRecord(DecimalFloatMixin, SchemaBase):
    id: Optional[int] = None
    district_id: Optional[int] = None
    crop_id: Optional[int] = None
    year: int
    production_mt: Optional[float] = None
    area_harvested_ha: Optional[float] = None
    yield_kg_ha: Optional[float] = None
    data_source: Optional[str] = None
    data_quality: str = "Estimated"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class YieldStatistics(SchemaBase):
    avg_yield_kg_ha: Optional[float] = None
    max_yield_kg_ha: Optional[float] = None
    min_yield_kg_ha: Optional[float] = None
    volatility: Optional[float] = None
    cagr_pct: Optional[float] = None
    trend: Optional[str] = None


class YieldTimeseriesResponse(SchemaBase):
    district_id: int
    district_name: str
    crop_id: int
    crop_name: str
    timeseries: list[YieldRecord]
    statistics: YieldStatistics


class DistrictYieldsResponse(SchemaBase):
    district_id: int
    district_name: str
    year: int
    crops: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Climate schemas
# ---------------------------------------------------------------------------


class ClimateRecord(DecimalFloatMixin, SchemaBase):
    id: Optional[int] = None
    district_id: Optional[int] = None
    observation_date: Union[str, date]
    rainfall_mm: Optional[float] = None
    temperature_min_c: Optional[float] = None
    temperature_max_c: Optional[float] = None
    temperature_mean_c: Optional[float] = None
    solar_radiation_mj_m2: Optional[float] = None
    data_source: Optional[str] = None
    created_at: Optional[str] = None


class ClimateSummary(SchemaBase):
    annual_rainfall_mm: Optional[float] = None
    avg_temperature_c: Optional[float] = None
    monsoon_start_month: Optional[int] = None
    monsoon_end_month: Optional[int] = None


class ClimateResponse(SchemaBase):
    district_id: int
    district_name: str
    data: list[ClimateRecord]
    summary: ClimateSummary


# ---------------------------------------------------------------------------
# Correlation schemas
# ---------------------------------------------------------------------------


class CorrelationComponent(SchemaBase):
    coefficient: Optional[float] = None
    p_value: Optional[float] = None
    significant: bool = False


class CorrelationResult(SchemaBase):
    coefficient: Optional[float] = None
    p_value: Optional[float] = None
    r_squared: Optional[float] = None
    sample_size: Optional[int] = None
    significant: bool = False


class CorrelationResponse(SchemaBase):
    district_id: int
    district_name: str
    crop_id: int
    crop_name: str
    lag_months: int = 0
    correlations: dict[str, CorrelationComponent]
    r_squared: Optional[float] = None
    interpretation: Optional[str] = None


# ---------------------------------------------------------------------------
# Export crop schemas
# ---------------------------------------------------------------------------


class ExportSeason(SchemaBase):
    start_month: int
    end_month: int
    peak_month: Optional[int] = None


class ExportCropInfo(SchemaBase):
    crop_id: int
    crop_name: str
    production_mt: Optional[float] = None
    area_harvested_ha: Optional[float] = None
    yield_kg_ha: Optional[float] = None
    export_potential_mt: Optional[float] = None
    avg_price_usd_per_mt: Optional[float] = None
    estimated_revenue_usd: Optional[float] = None
    export_season: Optional[ExportSeason] = None
    main_export_countries: list[str] = []


class ExportCropsResponse(SchemaBase):
    district_id: int
    year: int
    export_crops: list[ExportCropInfo]
    total_export_revenue_usd: Optional[float] = None


# ---------------------------------------------------------------------------
# Commercialization schemas
# ---------------------------------------------------------------------------


class CommercializationComponents(SchemaBase):
    export_crop_contribution: Optional[float] = None
    farm_size_contribution: Optional[float] = None
    export_volume_contribution: Optional[float] = None


class CommercializationResponse(SchemaBase):
    district_id: int
    district_name: str
    year: int
    export_crop_area_pct: Optional[float] = None
    subsistence_area_pct: Optional[float] = None
    other_area_pct: Optional[float] = None
    avg_holding_size_ha: Optional[float] = None
    export_volume_ratio: Optional[float] = None
    commercialization_score: Optional[float] = None
    commercialization_level: Optional[str] = None
    components: Optional[CommercializationComponents] = None


class CommercializationRankResponse(SchemaBase):
    rank: int
    district_name: str
    district_id: int
    commercialization_score: float
    export_crop_area_pct: Optional[float] = None
    subsistence_area_pct: Optional[float] = None
    commercialization_level: Optional[str] = None
    province: Optional[str] = None


class CommercializationRankingsResponse(SchemaBase):
    year: int
    total: int
    districts: list[CommercializationRankResponse]


# ---------------------------------------------------------------------------
# Forecast schemas
# ---------------------------------------------------------------------------


class ForecastMonth(SchemaBase):
    forecast_month: str
    forecast_yield_kg_ha: Optional[float] = None
    lower_ci_95: Optional[float] = None
    upper_ci_95: Optional[float] = None
    forecast_model: Optional[str] = None
    forecast_date: Optional[str] = None
    confidence: float = 0.95


class ModelDiagnostics(SchemaBase):
    rmse_kg_ha: Optional[float] = None
    mae_kg_ha: Optional[float] = None
    mape_pct: Optional[float] = None


class ForecastResponse(SchemaBase):
    district_id: int
    district_name: str
    crop_id: int
    crop_name: str
    forecast_horizon_months: int
    forecast_model: Optional[str] = None
    model_diagnostics: ModelDiagnostics
    forecasts: list[ForecastMonth]
    recommendation: Optional[str] = None


# ---------------------------------------------------------------------------
# Heatmap schemas
# ---------------------------------------------------------------------------


class HeatmapRow(SchemaBase):
    district: str
    district_id: int
    crop: str
    crop_id: int
    rainfall_corr: Optional[float] = None
    temperature_corr: Optional[float] = None
    solar_corr: Optional[float] = None


class HeatmapResponse(SchemaBase):
    total_rows: int
    rows: list[HeatmapRow]


# ---------------------------------------------------------------------------
# Error / health schemas
# ---------------------------------------------------------------------------


class ErrorResponse(SchemaBase):
    error: dict[str, Any]


class HealthResponse(SchemaBase):
    status: str
    timestamp: str
    database: str
