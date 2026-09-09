"""
Filter validation service.

Pre-computes valid filter values from the DB once per request and caches
them so repeated checks don't trigger N+1 queries.
"""

from __future__ import annotations

from functools import cached_property
from typing import Annotated

from api.db import get_db
from api.models.db_models import Districts
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session


class FilterValidator:
    """Validate filter values against cached DB lookups.

    Usage:
        validator = FilterValidator(db)
        if not validator.validate_province("Eastern"):
            raise HTTPException(status_code=400, detail="Invalid province")
    """

    def __init__(self, db: Session):
        self.db = db

    @cached_property
    def provinces(self) -> set[str]:
        return {
            v
            for v in self.db.execute(
                select(Districts.province).where(Districts.province.isnot(None))
            )
            .scalars()
            .all()
            if v is not None
        }

    @cached_property
    def regions(self) -> set[str]:
        return {
            v
            for v in self.db.execute(
                select(Districts.region).where(Districts.region.isnot(None))
            )
            .scalars()
            .all()
            if v is not None
        }

    @cached_property
    def district_ids(self) -> set[int]:
        return set(self.db.execute(select(Districts.id)).scalars().all())

    def validate_province(self, province: str) -> bool:
        if not province or not isinstance(province, str):
            return False
        return province.strip() in self.provinces

    def validate_region(self, region: str) -> bool:
        if not region or not isinstance(region, str):
            return False
        return region.strip() in self.regions

    # ponytail: validate_crop_id removed — no route validates crop ID via this validator;
    # routes use db.get(Crops, id) directly and return 404 if missing.

    def validate_district_id(self, district_id: int) -> bool:
        """Check if district exists."""
        if not isinstance(district_id, int) or district_id <= 0:
            return False
        return district_id in self.district_ids

    def get_provinces(self) -> set[str]:
        return self.provinces

    def get_regions(self) -> set[str]:
        return self.regions


def get_filter_validator(db: Annotated[Session, Depends(get_db)]) -> FilterValidator:
    """Return a request-scoped filter validator (caches within one request)."""
    return FilterValidator(db)
