"""
SQLAlchemy ORM models for the Nepal Agricultural Intelligence Dashboard.

Defines all database tables, constants referenced by the ETL pipeline,
and the shared ``Base`` used by both the ORM models and the ETL upsert logic.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    ARRAY,
    DECIMAL,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

__all__ = [
    "MAX_SUPPORTED_HARVEST_YEAR",
    "MIN_SUPPORTED_HARVEST_YEAR",
    "MISSING_DATA_SOURCE",
    "Base",
    "Climate",
    "CommercializationIndex",
    "Crops",
    "Districts",
    "ExportCrops",
    "Forecasts",
    "Yields",
]

# ---------------------------------------------------------------------------
# Constants referenced by services/etl.py and tests
# ---------------------------------------------------------------------------

MISSING_DATA_SOURCE: str = "UNKNOWN"
MIN_SUPPORTED_HARVEST_YEAR: int = 2014
MAX_SUPPORTED_HARVEST_YEAR: int = 2024

# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------

convention = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(referred_table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return (
            cls.__name__.lower() + "s"
            if not cls.__name__.lower().endswith("s")
            else cls.__name__.lower()
        )


# ---------------------------------------------------------------------------
# Districts
# ---------------------------------------------------------------------------


class Districts(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    province: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[str | None] = mapped_column(String(50))
    latitude: Mapped[float | None] = mapped_column(DECIMAL(10, 8))
    longitude: Mapped[float | None] = mapped_column(DECIMAL(11, 8))
    population: Mapped[int | None] = mapped_column(Integer)
    area_sq_km: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ---------------------------------------------------------------------------
# Crops
# ---------------------------------------------------------------------------


class Crops(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    fao_code: Mapped[str | None] = mapped_column(String(10))
    category: Mapped[str | None] = mapped_column(String(50))
    unit: Mapped[str] = mapped_column(String(20), default="MT")
    is_export_crop: Mapped[bool] = mapped_column(Boolean, default=False)
    is_subsistence: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ---------------------------------------------------------------------------
# Yields (fact table)
# ---------------------------------------------------------------------------


class Yields(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(
        ForeignKey("districts.id", ondelete="CASCADE")
    )
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"))
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    production_mt: Mapped[float | None] = mapped_column(DECIMAL(15, 2))
    area_harvested_ha: Mapped[float | None] = mapped_column(DECIMAL(15, 2))
    yield_kg_ha: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    data_source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default=MISSING_DATA_SOURCE,
        default=MISSING_DATA_SOURCE,
    )
    data_quality: Mapped[str] = mapped_column(String(20), default="Estimated")
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    district: Mapped[Districts | None] = relationship("Districts", backref="yields")
    crop: Mapped[Crops | None] = relationship("Crops", backref="yields")

    __table_args__ = (
        UniqueConstraint(
            "district_id",
            "crop_id",
            "year",
            "data_source",
            name="uq_yields_district_crop_year_source",
        ),
    )


# ---------------------------------------------------------------------------
# Climate (fact table)
# ---------------------------------------------------------------------------


class Climate(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(
        ForeignKey("districts.id", ondelete="CASCADE")
    )
    observation_date: Mapped[date] = mapped_column(nullable=False)
    rainfall_mm: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    temperature_min_c: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    temperature_max_c: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    temperature_mean_c: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    solar_radiation_mj_m2: Mapped[float | None] = mapped_column(DECIMAL(8, 2))
    data_source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default=MISSING_DATA_SOURCE,
        default=MISSING_DATA_SOURCE,
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    district: Mapped[Districts | None] = relationship("Districts", backref="climate")

    __table_args__ = (
        UniqueConstraint(
            "district_id",
            "observation_date",
            "data_source",
            name="uq_climate_district_date_source",
        ),
    )


# ---------------------------------------------------------------------------
# Export crops (dimension table)
# ---------------------------------------------------------------------------


class ExportCrops(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        ForeignKey("crops.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    main_export_countries: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    avg_price_usd_per_mt: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    export_season_start_month: Mapped[int | None] = mapped_column(Integer)
    export_season_end_month: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    crop: Mapped[Crops | None] = relationship("Crops", backref="export_crop")


# ---------------------------------------------------------------------------
# Commercialization index (computed table)
# ---------------------------------------------------------------------------


class CommercializationIndex(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(
        ForeignKey("districts.id", ondelete="CASCADE")
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    export_crop_area_pct: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    subsistence_area_pct: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    avg_holding_size_ha: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    export_volume_ratio: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    commercialization_score: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    district: Mapped[Districts | None] = relationship(
        "Districts", backref="commercialization_index"
    )

    __table_args__ = (
        UniqueConstraint(
            "district_id",
            "year",
            name="uq_commercialization_district_year",
        ),
    )


# ---------------------------------------------------------------------------
# Forecasts (precomputed table)
# ---------------------------------------------------------------------------


class Forecasts(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(
        ForeignKey("districts.id", ondelete="CASCADE")
    )
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"))
    forecast_month: Mapped[date] = mapped_column(nullable=False)
    forecast_yield_kg_ha: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    lower_ci_95: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    upper_ci_95: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    forecast_model: Mapped[str | None] = mapped_column(String(50))
    rmse_kg_ha: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    mae_kg_ha: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    mape_pct: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    forecast_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    district: Mapped[Districts | None] = relationship("Districts", backref="forecasts")
    crop: Mapped[Crops | None] = relationship("Crops", backref="forecasts")

    __table_args__ = (
        UniqueConstraint(
            "district_id",
            "crop_id",
            "forecast_month",
            "forecast_model",
            name="uq_forecasts_district_crop_month_model",
        ),
    )
