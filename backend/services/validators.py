"""
Filter validation and sanitization service.

Prevents N+1 queries by pre-computing and caching valid filter values.
Cache is session-scoped, so it's fresh per request but doesn't require DB hits per filter check.
"""

from collections.abc import Sequence
from typing import Annotated

from api.models.db_models import Crops, Districts
from fastapi import Depends
from sqlalchemy import distinct, select
from sqlalchemy.orm import Session
from test_minimal import get_db


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
        self._provinces_cache: set[str] | None = None
        self._regions_cache: set[str] | None = None
        self._crop_ids_cache: set[int] | None = None
        self._district_ids_cache: set[int] | None = None

    def _get_provinces(self) -> set[str]:
        """Lazy-load provinces from cache or DB (once per session)."""
        if self._provinces_cache is None:
            results: Sequence[str | None] = (
                self.db.execute(
                    select(distinct(Districts.province))
                    .where(Districts.province.isnot(None))
                    .order_by(Districts.province)
                )
                .scalars()
                .all()
            )
            # Filter out None values for type safety
            self._provinces_cache = {r for r in results if r is not None}
        return self._provinces_cache

    def _get_regions(self) -> set[str]:
        """Lazy-load regions from cache or DB (once per session)."""
        if self._regions_cache is None:
            results: Sequence[str | None] = (
                self.db.execute(
                    select(distinct(Districts.region))
                    .where(Districts.region.isnot(None))
                    .order_by(Districts.region)
                )
                .scalars()
                .all()
            )
            # Filter out None values for type safety
            self._regions_cache = {r for r in results if r is not None}
        return self._regions_cache

    def _get_crop_ids(self) -> set[int]:
        """Lazy-load crop IDs from cache or DB (once per session)."""
        if self._crop_ids_cache is None:
            results: Sequence[int] = self.db.execute(select(Crops.id)).scalars().all()
            self._crop_ids_cache = set(results)
        return self._crop_ids_cache

    def _get_district_ids(self) -> set[int]:
        """Lazy-load district IDs from cache or DB (once per session)."""
        if self._district_ids_cache is None:
            results: Sequence[int] = (
                self.db.execute(select(Districts.id)).scalars().all()
            )
            self._district_ids_cache = set(results)
        return self._district_ids_cache

    def get_provinces(self) -> set[str]:
        """Get all valid province values."""
        return self._get_provinces()

    def get_regions(self) -> set[str]:
        """Get all valid region values."""
        return self._get_regions()

    def get_crop_ids(self) -> set[int]:
        """Get all valid crop IDs."""
        return self._get_crop_ids()

    def get_district_ids(self) -> set[int]:
        """Get all valid district IDs."""
        return self._get_district_ids()

    def validate_province(self, province: str) -> bool:
        """
        Check if province is valid.

        Args:
            province: Province name to validate

        Returns:
            True if province exists, False otherwise
        """
        if not province or not isinstance(province, str):
            return False
        return province.strip() in self._get_provinces()

    def validate_region(self, region: str) -> bool:
        """
        Check if region is valid.

        Args:
            region: Region name to validate

        Returns:
            True if region exists, False otherwise
        """
        if not region or not isinstance(region, str):
            return False
        return region.strip() in self._get_regions()

    def validate_crop_id(self, crop_id: int) -> bool:
        """
        Check if crop_id exists.

        Args:
            crop_id: Crop ID to validate

        Returns:
            True if crop exists, False otherwise
        """
        if not isinstance(crop_id, int) or crop_id <= 0:
            return False
        return crop_id in self._get_crop_ids()

    def validate_district_id(self, district_id: int) -> bool:
        """
        Check if district_id exists.

        Args:
            district_id: District ID to validate

        Returns:
            True if district exists, False otherwise
        """
        if not isinstance(district_id, int) or district_id <= 0:
            return False
        return district_id in self._get_district_ids()


def get_filter_validator(db: Annotated[Session, Depends(get_db)]) -> FilterValidator:
    """
    FastAPI dependency to inject filter validator into routes.

    Validator is session-scoped, so it's fresh per request but caches
    within that request to prevent multiple DB queries.

    Example:
        @app.get("/data")
        def get_data(
            validator: Annotated[FilterValidator, Depends(get_filter_validator)]
        ):
            if validator.validate_province("Eastern"):
                # do something
    """
    return FilterValidator(db)
