from typing import Annotated

from api.db import get_db
from api.models.db_models import (
    MAX_SUPPORTED_HARVEST_YEAR,
    MIN_SUPPORTED_HARVEST_YEAR,
    CommercializationIndex,
    Districts,
)
from api.models.schemas import (
    CommercializationComponents,
    CommercializationRankingsResponse,
    CommercializationRankResponse,
    CommercializationResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter()


def _level(score: float) -> str:
    """Map a commercialization score (0-100) to a label.

    Thresholds (matching test expectations):
      0-25   -> SUBSISTENCE
      26-50  -> MIXED
      51-75  -> COMMERCIAL
      76-100 -> HIGHLY_COMMERCIAL
    """
    if score <= 25:
        return "SUBSISTENCE"
    elif score <= 50:
        return "MIXED"
    elif score <= 75:
        return "COMMERCIAL"
    else:
        return "HIGHLY_COMMERCIAL"


@router.get(
    "/commercialization/{district_id}", response_model=CommercializationResponse
)
def get_commercialization(
    district_id: int,
    db: Annotated[Session, Depends(get_db)],
    year: int = Query(
        2024, ge=MIN_SUPPORTED_HARVEST_YEAR, le=MAX_SUPPORTED_HARVEST_YEAR
    ),
):
    district = db.get(Districts, district_id)
    if not district:
        raise HTTPException(
            status_code=404, detail=f"District with ID {district_id} not found"
        )

    record = db.execute(
        select(CommercializationIndex)
        .where(CommercializationIndex.district_id == district_id)
        .where(CommercializationIndex.year == year)
    ).scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No commercialization data for district {district.name} in {year}",
        )

    export_pct = float(record.export_crop_area_pct or 0)
    subsistence_pct = float(record.subsistence_area_pct or 0)
    other_pct = max(100 - export_pct - subsistence_pct, 0)

    holding = float(record.avg_holding_size_ha or 0)
    score = float(record.commercialization_score or 0)

    return CommercializationResponse(
        district_id=district_id,
        district_name=district.name,
        year=year,
        export_crop_area_pct=export_pct,
        subsistence_area_pct=subsistence_pct,
        other_area_pct=round(other_pct, 2),
        avg_holding_size_ha=holding,
        export_volume_ratio=float(record.export_volume_ratio or 0),
        commercialization_score=score,
        commercialization_level=_level(score),
        components=CommercializationComponents(
            export_crop_contribution=round(export_pct * 0.40, 2),
            farm_size_contribution=round(holding / 5.0 * 0.30, 2),
            export_volume_contribution=round(
                float(record.export_volume_ratio or 0) * 0.30, 2
            ),
        ),
    )


@router.get("/commercialization", response_model=CommercializationRankingsResponse)
def get_commercialization_rankings(
    db: Annotated[Session, Depends(get_db)],
    year: int = Query(
        2024, ge=MIN_SUPPORTED_HARVEST_YEAR, le=MAX_SUPPORTED_HARVEST_YEAR
    ),
    province: str | None = Query(None, description="Filter by province"),
    limit: int = Query(77, ge=1, le=77),
):
    stmt = (
        select(CommercializationIndex, Districts)
        .join(Districts)
        .where(CommercializationIndex.year == year)
        .order_by(CommercializationIndex.commercialization_score.desc())
        .limit(limit)
    )
    if province:
        stmt = stmt.where(Districts.province == province)

    results = db.execute(stmt).all()
    districts_list = []
    for idx, (ci, d) in enumerate(results):
        score = float(ci.commercialization_score or 0)
        districts_list.append(
            CommercializationRankResponse(
                rank=idx + 1,
                district_name=d.name,
                district_id=d.id,
                commercialization_score=score,
                export_crop_area_pct=float(ci.export_crop_area_pct or 0),
                subsistence_area_pct=float(ci.subsistence_area_pct or 0),
                commercialization_level=_level(score),
                province=d.province,
            )
        )

    return CommercializationRankingsResponse(
        year=year,
        total=len(districts_list),
        districts=districts_list,
    )
