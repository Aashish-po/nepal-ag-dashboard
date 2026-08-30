from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from services.correlations import calculate_yield_statistics
from services.validators import FilterValidator, get_filter_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db import get_db
from api.models.db_models import (
    MAX_SUPPORTED_HARVEST_YEAR,
    MIN_SUPPORTED_HARVEST_YEAR,
    Crops,
    Districts,
    Yields,
)
from api.models.schemas import (
    DistrictYieldsResponse,
    YieldRecord,
    YieldStatistics,
    YieldTimeseriesResponse,
)

router = APIRouter()


@router.get("/yields/{district_id}/{crop_id}", response_model=YieldTimeseriesResponse)
def get_yields(
    district_id: int,
    crop_id: int,
    db: Annotated[Session, Depends(get_db)],
    validator: Annotated[FilterValidator, Depends(get_filter_validator)],
    year_start: int = Query(
        2014,
        ge=MIN_SUPPORTED_HARVEST_YEAR,
        le=MAX_SUPPORTED_HARVEST_YEAR,
    ),
    year_end: int = Query(
        2024,
        ge=MIN_SUPPORTED_HARVEST_YEAR,
        le=MAX_SUPPORTED_HARVEST_YEAR,
    ),
):
    """Get yield timeseries for a specific district-crop pair."""

    if year_start > year_end:
        raise HTTPException(
            status_code=400,
            detail="year_start must be <= year_end",
        )

    # Validate district exists
    if not validator.validate_district_id(district_id):
        raise HTTPException(
            status_code=404,
            detail=f"District {district_id} not found",
        )

    # Validate crop exists
    if not validator.validate_crop_id(crop_id):
        raise HTTPException(
            status_code=404,
            detail=f"Crop {crop_id} not found",
        )

    # Get district & crop metadata (cached lookups now)
    district = db.get(Districts, district_id)
    crop = db.get(Crops, crop_id)

    # Query yields (efficient with index)
    stmt = (
        select(Yields)
        .where(Yields.district_id == district_id)
        .where(Yields.crop_id == crop_id)
        .where(Yields.year >= year_start)
        .where(Yields.year <= year_end)
        .order_by(Yields.year.asc())
    )

    results = db.execute(stmt).scalars().all()
    results_for_response = list(reversed(results))
    timeseries = [YieldRecord.model_validate(r) for r in results_for_response]

    stats_dict = calculate_yield_statistics(results)
    statistics = YieldStatistics(**stats_dict)

    return YieldTimeseriesResponse(
        district_id=district_id,
        district_name=district.name if district else "Unknown",
        crop_id=crop_id,
        crop_name=crop.name if crop else "Unknown",
        timeseries=timeseries,
        statistics=statistics,
    )


@router.get("/yields/{district_id}", response_model=DistrictYieldsResponse)
def get_district_yields(
    district_id: int,
    db: Annotated[Session, Depends(get_db)],
    validator: Annotated[FilterValidator, Depends(get_filter_validator)],
    year: int = Query(
        2024,
        ge=MIN_SUPPORTED_HARVEST_YEAR,
        le=MAX_SUPPORTED_HARVEST_YEAR,
    ),
):
    """Get all crop yields for a district in a given year."""

    if not validator.validate_district_id(district_id):
        raise HTTPException(
            status_code=404,
            detail=f"District {district_id} not found",
        )

    district = db.get(Districts, district_id)

    # Single optimized query: all yields for district + crop names, ordered
    stmt = (
        select(Yields, Crops)
        .join(Crops)
        .where(Yields.district_id == district_id)
        .order_by(Yields.crop_id, Yields.year.asc())
    )
    all_yields = db.execute(stmt).all()

    # Single-pass grouping
    yields_by_crop: dict[int, tuple[Crops, list[Yields]]] = {}

    for yield_record, crop_record in all_yields:
        if yield_record.crop_id not in yields_by_crop:
            yields_by_crop[yield_record.crop_id] = (crop_record, [])
        yields_by_crop[yield_record.crop_id][1].append(yield_record)

    # Build response
    crops_data = []
    for crop_id, (crop, crop_yields) in yields_by_crop.items():
        year_yield = next((y for y in crop_yields if y.year == year), None)
        if not year_yield:
            continue

        stats_dict = calculate_yield_statistics(crop_yields)
        stats = YieldStatistics(**stats_dict)

        crops_data.append(
            {
                "crop_id": crop_id,
                "crop_name": crop.name,
                "yield_kg_ha": float(year_yield.yield_kg_ha)
                if year_yield.yield_kg_ha is not None
                else None,
                "production_mt": float(year_yield.production_mt)
                if year_yield.production_mt is not None
                else None,
                "trend": stats.trend or "INSUFFICIENT_DATA",
                "cagr_pct": stats.cagr_pct,
            }
        )

    return DistrictYieldsResponse(
        district_id=district_id,
        district_name=district.name if district else "Unknown",
        year=year,
        crops=crops_data,
    )
