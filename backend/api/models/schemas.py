"""
Pydantic response schemas for the Nepal Agricultural Intelligence Dashboard.

All models are configured with ``from_attributes=True`` so SQLAlchemy ORM
objects can be serialized directly via ``model_validate``.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Shared config
# ---------------------------------------------------------------------------


class SchemaBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        protected_namespaces=(),
    )


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------


class DistrictResponse(SchemaBase):
    id: int
    name: str
    province: str
    region: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    population: int | None = None
    area_sq_km: float | None = None
    created_at: datetime | None = None


class DistrictListResponse(SchemaBase):
    total: int
    districts: list[DistrictResponse]


class CropResponse(SchemaBase):
    id: int
    name: str
    fao_code: str | None = None
    category: str | None = None
    unit: str | None = "MT"
    is_export_crop: bool | None = False
    is_subsistence: bool | None = False
    created_at: datetime | None = None


class CropListResponse(SchemaBase):
    total: int
    crops: list[CropResponse]


# ---------------------------------------------------------------------------
# Yield schemas
# ---------------------------------------------------------------------------


class YieldRecord(SchemaBase):
    id: int | None = None
    district_id: int | None = None
    crop_id: int | None = None
    year: int
    production_mt: float | None = None
    area_harvested_ha: float | None = None
    yield_kg_ha: float | None = None
    data_source: str | None = None
    data_quality: str = "Estimated"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class YieldStatistics(SchemaBase):
    avg_yield_kg_ha: float | None = None
    max_yield_kg_ha: float | None = None
    min_yield_kg_ha: float | None = None
    volatility: float | None = None
    cagr_pct: float | None = None
    trend: str | None = None


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


class ClimateRecord(SchemaBase):
    id: int | None = None
    district_id: int | None = None
    observation_date: str | date
    rainfall_mm: float | None = None
    temperature_min_c: float | None = None
    temperature_max_c: float | None = None
    temperature_mean_c: float | None = None
    solar_radiation_mj_m2: float | None = None
    data_source: str | None = None
    created_at: str | None = None


class ClimateSummary(SchemaBase):
    annual_rainfall_mm: float | None = None
    avg_temperature_c: float | None = None
    monsoon_start_month: int | None = None
    monsoon_end_month: int | None = None


class ClimateResponse(SchemaBase):
    district_id: int
    district_name: str
    data: list[ClimateRecord]
    summary: ClimateSummary


# ---------------------------------------------------------------------------
# Correlation schemas
# ---------------------------------------------------------------------------


class CorrelationComponent(SchemaBase):
    coefficient: float | None = None
    p_value: float | None = None
    significant: bool = False


class CorrelationResponse(SchemaBase):
    district_id: int
    district_name: str
    crop_id: int
    crop_name: str
    lag_months: int = 0
    correlations: dict[str, CorrelationComponent]
    r_squared: float | None = None
    interpretation: str | None = None


# ---------------------------------------------------------------------------
# Export crop schemas
# ---------------------------------------------------------------------------


class ExportSeason(SchemaBase):
    start_month: int
    end_month: int


class ExportCropInfo(SchemaBase):
    crop_id: int
    crop_name: str
    production_mt: float | None = None
    area_harvested_ha: float | None = None
    yield_kg_ha: float | None = None
    export_potential_mt: float | None = None
    avg_price_usd_per_mt: float | None = None
    estimated_revenue_usd: float | None = None
    export_season: ExportSeason | None = None
    main_export_countries: list[str] = []


class ExportCropsResponse(SchemaBase):
    district_id: int
    district_name: str
    year: int
    export_crops: list[ExportCropInfo]
    total_export_revenue_usd: float | None = None


# ---------------------------------------------------------------------------
# Commercialization schemas
# ---------------------------------------------------------------------------


class CommercializationComponents(SchemaBase):
    export_crop_contribution: float | None = None
    farm_size_contribution: float | None = None
    export_volume_contribution: float | None = None


class CommercializationResponse(SchemaBase):
    district_id: int
    district_name: str
    year: int
    export_crop_area_pct: float | None = None
    subsistence_area_pct: float | None = None
    other_area_pct: float | None = None
    avg_holding_size_ha: float | None = None
    export_volume_ratio: float | None = None
    commercialization_score: float | None = None
    commercialization_level: str | None = None
    components: CommercializationComponents | None = None


class CommercializationRankResponse(SchemaBase):
    rank: int
    district_name: str
    district_id: int
    commercialization_score: float
    export_crop_area_pct: float | None = None
    subsistence_area_pct: float | None = None
    commercialization_level: str | None = None
    province: str | None = None


class CommercializationRankingsResponse(SchemaBase):
    year: int
    total: int
    districts: list[CommercializationRankResponse]


# ---------------------------------------------------------------------------
# Forecast schemas
# ---------------------------------------------------------------------------


class ForecastMonth(SchemaBase):
    forecast_month: str
    forecast_yield_kg_ha: float | None = None
    lower_ci_95: float | None = None
    upper_ci_95: float | None = None
    forecast_model: str | None = None
    forecast_date: str | None = None


class ModelDiagnostics(SchemaBase):
    rmse_kg_ha: float | None = None
    mae_kg_ha: float | None = None
    mape_pct: float | None = None


class ForecastResponse(SchemaBase):
    district_id: int
    district_name: str
    crop_id: int
    crop_name: str
    forecast_horizon_months: int
    forecast_model: str | None = None
    model_diagnostics: ModelDiagnostics
    forecasts: list[ForecastMonth]
    recommendation: str | None = None


# ---------------------------------------------------------------------------
# Heatmap schemas
# ---------------------------------------------------------------------------


class HeatmapRow(SchemaBase):
    district: str
    district_id: int
    crop: str
    crop_id: int
    rainfall_corr: float | None = None
    temperature_corr: float | None = None
    solar_corr: float | None = None


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
