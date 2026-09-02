"""
SQLAlchemy ORM and Pydantic schema re-exports for the API.

This module aggregates the core models and response schemas used across
the FastAPI routes and the ETL pipeline, so that any module can do::

    from backend.api.models import Districts, Yields, HealthResponse
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# DB models (from api.models.db_models)
# ---------------------------------------------------------------------------
from .db_models import (
    MAX_SUPPORTED_HARVEST_YEAR,
    MIN_SUPPORTED_HARVEST_YEAR,
    MISSING_DATA_SOURCE,
    Base,
    Climate,
    CommercializationIndex,
    Crops,
    Districts,
    ExportCrops,
    Forecasts,
    Yields,
)

# ---------------------------------------------------------------------------
# Pydantic schemas (from api.models.schemas)
# ---------------------------------------------------------------------------
from .schemas import (
    ClimateRecord,
    ClimateResponse,
    ClimateSummary,
    CommercializationComponents,
    CommercializationRankingsResponse,
    CommercializationRankResponse,
    CommercializationResponse,
    CorrelationComponent,
    CorrelationResponse,
    CropListResponse,
    CropResponse,
    DistrictListResponse,
    DistrictResponse,
    ExportCropInfo,
    ExportCropsResponse,
    ExportSeason,
    ForecastMonth,
    ForecastResponse,
    HealthResponse,
    ModelDiagnostics,
    YieldRecord,
    YieldStatistics,
    YieldTimeseriesResponse,
)

__all__ = [
    # Constants
    "MAX_SUPPORTED_HARVEST_YEAR",
    "MIN_SUPPORTED_HARVEST_YEAR",
    "MISSING_DATA_SOURCE",
    # ORM models
    "Base",
    "Climate",
    "ClimateRecord",
    "ClimateResponse",
    "ClimateSummary",
    "CommercializationComponents",
    "CommercializationIndex",
    "CommercializationRankResponse",
    "CommercializationRankingsResponse",
    "CommercializationResponse",
    "CorrelationComponent",
    "CorrelationResponse",
    "CropListResponse",
    "CropResponse",
    "Crops",
    "DistrictListResponse",
    "DistrictResponse",
    "Districts",
    "ExportCropInfo",
    "ExportCrops",
    "ExportCropsResponse",
    "ExportSeason",
    "ForecastMonth",
    "ForecastResponse",
    "Forecasts",
    # Pydantic schemas
    "HealthResponse",
    "ModelDiagnostics",
    "YieldRecord",
    "YieldStatistics",
    "YieldTimeseriesResponse",
    "Yields",
]
