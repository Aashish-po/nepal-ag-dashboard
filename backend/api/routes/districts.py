from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db import get_db
from api.models.db_models import Districts
from api.models.schemas import DistrictListResponse, DistrictResponse

router = APIRouter()


@router.get("/districts", response_model=DistrictListResponse)
def get_districts(
    db: Session = Depends(get_db),
    province: str | None = Query(None, description="Filter by province"),
    region: str | None = Query(None, description="Filter by region"),
):
    stmt = select(Districts)
    if province:
        stmt = stmt.where(Districts.province == province)
    if region:
        stmt = stmt.where(Districts.region == region)

    results = db.execute(stmt).scalars().all()
    districts = [DistrictResponse.model_validate(d) for d in results]
    return DistrictListResponse(total=len(districts), districts=districts)


@router.get("/districts/search", response_model=DistrictListResponse)
def search_districts(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    db: Session = Depends(get_db),
):
    pattern = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    stmt = select(Districts).where(Districts.name.ilike(f"%{pattern}%", escape="\\"))
    results = db.execute(stmt).scalars().all()
    districts = [DistrictResponse.model_validate(d) for d in results]
    return DistrictListResponse(total=len(districts), districts=districts)
