"""
Filter validation and sanitization service.

Prevents N+1 queries by pre-computing and caching valid filter values.
Cache is session-scoped, so it's fresh per request but doesn't require DB hits per filter check.
"""

from collections.abc import Sequence
from typing import Annotated

from api.db import get_db
from api.models.db_models import Crops, Districts
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session


class FilterValidator:
    """
    Validate and cache filter values to prevent N+1 queries.

    Usage:
        validator = FilterValidator(db)
        if not validator.validate_province("Eastern"):
            raise HTTPException(status_code=400, detail="Invalid province")
    """

    def __init__(self, db: Session):
        self.db = db
        # Session-scoped cache: populated on first access
        self._provinces_cache: set[str | int] | None = None
        self._regions_cache: set[str | int] | None = None
        self._crop_ids_cache: set[int] | None = None
        self._district_ids_cache: set[int] | None = None

    def _get_values(self, table_model, column_name: str) -> set[str | int]:
        """Lazy-load distinct non-null values from a column (once per session)."""
        cache_attr = f"_{column_name.lower()}_cache"
        cached = getattr(self, cache_attr, None)
        if cached is None:
            column = getattr(table_model, column_name)
            stmt = select(column).where(column.isnot(None)).order_by(column)
            results: Sequence[str | int | None] = self.db.execute(stmt).scalars().all()
            result_set = {v for v in results if v is not None}
            setattr(self, cache_attr, result_set)
            return result_set
        return cached

    def _get_ids(self, table_model) -> set[int]:
        """Lazy-load distinct IDs from a model (once per session)."""
        cache_attr = f"_ids_{table_model.__name__.lower()}_cache"
        cached = getattr(self, cache_attr, None)
        if cached is None:
            stmt = select(table_model.id)
            results: Sequence[int] = self.db.execute(stmt).scalars().all()
            result_set = set(results)
            setattr(self, cache_attr, result_set)
            return result_set
        return cached

    def validate_province(self, province: str) -> bool:
        """Check if province exists."""
        if not province or not isinstance(province, str):
            return False
        return province.strip() in self._get_values(Districts, "province")

    def validate_region(self, region: str) -> bool:
        """Check if region exists."""
        if not region or not isinstance(region, str):
            return False
        return region.strip() in self._get_values(Districts, "region")

    def validate_crop_id(self, crop_id: int) -> bool:
        """Check if crop exists."""
        if not isinstance(crop_id, int) or crop_id <= 0:
            return False
        return crop_id in self._get_ids(Crops)

    def validate_district_id(self, district_id: int) -> bool:
        """Check if district exists."""
        if not isinstance(district_id, int) or district_id <= 0:
            return False
        return district_id in self._get_ids(Districts)

    def get_provinces(self) -> set[str]:
        return {
            v for v in self._get_values(Districts, "province") if isinstance(v, str)
        }  # type: ignore[arg-type]

    def get_regions(self) -> set[str]:
        return {v for v in self._get_values(Districts, "region") if isinstance(v, str)}  # type: ignore[arg-type]

    def get_crop_ids(self) -> set[int]:
        return self._get_ids(Crops)

    def get_district_ids(self) -> set[int]:
        return self._get_ids(Districts)


def get_filter_validator(db: Annotated[Session, Depends(get_db)]) -> FilterValidator:
    """Return a session-scoped filter validator (caches within one request)."""
    return FilterValidator(db)
