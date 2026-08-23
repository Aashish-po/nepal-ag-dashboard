from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.db import get_db
from api.models.db_models import Crops, Districts, Yields
from api.models.schemas import CorrelationComponent, CorrelationResponse

router = APIRouter()


@router.get("/correlation/{district_id}", response_model=CorrelationResponse)
def get_correlation(
    district_id: int,
    db: Annotated[Session, Depends(get_db)],
    crop_id: int | None = Query(
        None, description="Crop ID (defaults to top crop for district)"
    ),
    lag_months: int = Query(
        0, ge=0, le=60, description="Lag months (must be multiple of 12)"
    ),
):
    if lag_months % 12 != 0:
        raise HTTPException(
            status_code=400, detail="lag_months must be a multiple of 12"
        )

    district = db.get(Districts, district_id)
    if not district:
        raise HTTPException(
            status_code=404, detail=f"District with ID {district_id} not found"
        )

    # Determine crop (default to the district's most-recorded crop)
    if crop_id is None:
        stmt = (
            select(Yields.crop_id)
            .where(Yields.district_id == district_id)
            .where(Yields.yield_kg_ha.isnot(None))
            .group_by(Yields.crop_id)
            .order_by(func.count(Yields.year).desc())
            .limit(1)
        )
        crop_id = db.execute(stmt).scalar()
        if not crop_id:
            raise HTTPException(
                status_code=404, detail="No yield data for this district"
            )

    crop = db.get(Crops, crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop with ID {crop_id} not found")

    # Fetch yield data
    yield_stmt = (
        select(Yields)
        .where(Yields.district_id == district_id)
        .where(Yields.crop_id == crop_id)
        .where(Yields.yield_kg_ha.isnot(None))
        .order_by(Yields.year)
    )
    yield_results = db.execute(yield_stmt).scalars().all()

    if len(yield_results) < 3:
        raise HTTPException(
            status_code=400,
            detail="Insufficient yield data for correlation analysis (need >= 3 years)",
        )

    yield_years = [int(r.year) for r in yield_results]
    yield_values = [
        float(r.yield_kg_ha) for r in yield_results if r.yield_kg_ha is not None
    ]

    # Compute correlation using service functions
    from services.correlations import compute_yield_climate_correlation

    result = compute_yield_climate_correlation(
        district_id=district_id,
        crop_id=crop_id,
        yield_years=yield_years,
        yield_values=yield_values,
        lag_months=lag_months,
        db=db,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Insufficient climate data for correlation analysis",
        )

    # Build response
    correlations = {}
    for var, data in result["correlations"].items():
        correlations[var] = CorrelationComponent(**data)

    return CorrelationResponse(
        district_id=district_id,
        district_name=district.name,
        crop_id=crop_id,
        crop_name=crop.name,
        lag_months=lag_months,
        correlations=correlations,
        r_squared=result.get("r_squared"),
        interpretation=result.get("interpretation"),
    )
