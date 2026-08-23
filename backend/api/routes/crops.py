from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db import get_db
from api.models.db_models import Crops
from api.models.schemas import CropListResponse, CropResponse

router = APIRouter()


@router.get("/crops", response_model=CropListResponse)
def get_crops(
    db: Annotated[Session, Depends(get_db)],
    category: str | None = Query(None, description="Filter by category"),
    is_export_crop: bool | None = Query(None, description="Filter by export status"),
):
    stmt = select(Crops)
    if category:
        stmt = stmt.where(Crops.category == category)
    if is_export_crop is not None:
        stmt = stmt.where(Crops.is_export_crop == is_export_crop)

    results = db.execute(stmt).scalars().all()
    crops = [CropResponse.model_validate(c) for c in results]
    return CropListResponse(total=len(crops), crops=crops)
