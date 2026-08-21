from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db import get_db
from api.models.db_models import (
    Crops,
    Districts,
    Yields,
    MIN_SUPPORTED_HARVEST_YEAR,
    MAX_SUPPORTED_HARVEST_YEAR,
)
from api.models.schemas import (
    DistrictYieldsResponse,
    YieldRecord,
    YieldStatistics,
    YieldTimeseriesResponse,
)
from services.correlations import calculate_yield_statistics

router = APIRouter()


@router.get("/yields/{district_id}/{crop_id}", response_model=YieldTimeseriesResponse)
def get_yields(
    district_id: int,
    crop_id: int,
    db: Session = Depends(get_db),
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
    if year_start > year_end:
        raise HTTPException(
            status_code=400,
            detail="year_start must be <= year_end",
        )

    district = db.get(Districts, district_id)
    if not district:
        raise HTTPException(
            status_code=404,
            detail=f"District with ID {district_id} not found",
        )

    crop = db.get(Crops, crop_id)
    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Crop with ID {crop_id} not found",
        )

    # Query yields in ascending year order for statistics calculation
    stmt = (
        select(Yields)
        .where(Yields.district_id == district_id)
        .where(Yields.crop_id == crop_id)
        .where(Yields.year >= year_start)
        .where(Yields.year <= year_end)
        .order_by(Yields.year.asc())
    )

    results = db.execute(stmt).scalars().all()

    # Reverse for response (newest first)
    results_for_response = list(reversed(results))

    timeseries = [YieldRecord.model_validate(r) for r in results_for_response]

    # Convert to compatible format for statistics calculation (chronological order)
    class YieldPoint:
        def __init__(self, year: int, yield_kg_ha: float | None):
            self.year = year
            self.yield_kg_ha = yield_kg_ha

    yield_points = [
        YieldPoint(year=r.year, yield_kg_ha=float(r.yield_kg_ha) if r.yield_kg_ha is not None else None)
        for r in results
    ]
    stats_dict = calculate_yield_statistics(yield_points)
    statistics = YieldStatistics(**stats_dict)

    return YieldTimeseriesResponse(
        district_id=district_id,
        district_name=district.name,
        crop_id=crop_id,
        crop_name=crop.name,
        timeseries=timeseries,
        statistics=statistics,
    )


@router.get("/yields/{district_id}", response_model=DistrictYieldsResponse)
def get_district_yields(
    district_id: int,
    db: Session = Depends(get_db),
    year: int = Query(
        2024,
        ge=MIN_SUPPORTED_HARVEST_YEAR,
        le=MAX_SUPPORTED_HARVEST_YEAR,
    ),
):
    district = db.get(Districts, district_id)
    if not district:
        raise HTTPException(
            status_code=404,
            detail=f"District with ID {district_id} not found",
        )

    # Load the district's full yield history once
    history_stmt = (
        select(Yields)
        .where(Yields.district_id == district_id)
        .order_by(Yields.crop_id, Yields.year.asc())
    )
    history_results = db.execute(history_stmt).scalars().all()

    # Group records by crop_id
    from collections import defaultdict

    yields_by_crop: dict[int, list[Yields]] = defaultdict(list)
    for y in history_results:
        yields_by_crop[y.crop_id].append(y)

    # Get yields for the requested year for response
    year_stmt = (
        select(Yields, Crops)
        .join(Crops)
        .where(Yields.district_id == district_id)
        .where(Yields.year == year)
    )
    year_results = db.execute(year_stmt).all()

    crops_data = []

    for y, c in year_results:
        # Get full history for this crop
        crop_history = yields_by_crop.get(y.crop_id, [])

        class YieldPoint:
            def __init__(self, year: int, yield_kg_ha: float | None):
                self.year = year
                self.yield_kg_ha = yield_kg_ha

        yield_points = [
            YieldPoint(year=r.year, yield_kg_ha=float(r.yield_kg_ha) if r.yield_kg_ha is not None else None)
            for r in crop_history
        ]
        stats_dict = calculate_yield_statistics(yield_points)
        stats = YieldStatistics(**stats_dict)

        crops_data.append(
            {
                "crop_id": y.crop_id,
                "crop_name": c.name,
                "yield_kg_ha": float(y.yield_kg_ha)
                if y.yield_kg_ha is not None
                else None,
                "production_mt": float(y.production_mt)
                if y.production_mt is not None
                else None,
                "trend": stats.trend or "INSUFFICIENT_DATA",
                "cagr_pct": stats.cagr_pct,
            }
        )

    return DistrictYieldsResponse(
        district_id=district_id,
        district_name=district.name,
        year=year,
        crops=crops_data,
    )
