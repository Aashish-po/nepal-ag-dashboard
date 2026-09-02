"""
Districts API routes with validation and filtering.
"""

from typing import Annotated

from api.db import get_db
from api.models.db_models import Districts
from api.models.schemas import DistrictListResponse, DistrictResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from services.validators import FilterValidator, get_filter_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/districts", response_model=DistrictListResponse)
def get_districts(
    db: Annotated[Session, Depends(get_db)],
    validator: Annotated[FilterValidator, Depends(get_filter_validator)],
    province: str | None = Query(
        None,
        max_length=100,
        description="Filter by province name (case-sensitive, exact match)",
    ),
    region: str | None = Query(
        None,
        max_length=100,
        description="Filter by geographic region (case-sensitive, exact match)",
    ),
):
    """
    List all 77 districts with optional filtering.

    **Query Parameters:**
    - `province`: Filter by province (e.g., "Eastern", "Western")
    - `region`: Filter by region (e.g., "Tarai", "Hill", "Mountain")

    **Response:**
    Returns list of districts matching filters (or all districts if no filters).

    **Examples:**
    ```
    GET /api/v1/districts
    GET /api/v1/districts?province=Eastern
    GET /api/v1/districts?region=Tarai
    GET /api/v1/districts?province=Central&region=Hill
    ```
    """
    stmt = select(Districts).order_by(Districts.name.asc())

    # Validate and apply province filter
    if province:
        province = province.strip()
        if not province:  # Empty after strip
            raise HTTPException(
                status_code=400, detail="Province filter cannot be empty/whitespace"
            )
        if not validator.validate_province(province):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid province: '{province}'. "
                    "Use GET /api/v1/districts/provinces for valid values."
                ),
            )
        stmt = stmt.where(Districts.province == province)

    # Validate and apply region filter
    if region:
        region = region.strip()
        if not region:  # Empty after strip
            raise HTTPException(
                status_code=400, detail="Region filter cannot be empty/whitespace"
            )
        if not validator.validate_region(region):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid region: '{region}'. "
                    "Use GET /api/v1/districts/regions for valid values."
                ),
            )
        stmt = stmt.where(Districts.region == region)

    # Execute query (uses indexes)
    results = db.execute(stmt).scalars().all()
    districts = [DistrictResponse.model_validate(d) for d in results]

    return DistrictListResponse(total=len(districts), districts=districts)


@router.get("/districts/provinces", response_model=dict)
def get_provinces(
    validator: Annotated[FilterValidator, Depends(get_filter_validator)],
):
    """
    Get all valid province values.

    **Use this to:** Discover valid province filter values before querying.

    **Response:**
    ```json
    {
        "provinces": ["Central", "Eastern", "Western", ...],
        "count": 5
    }
    ```
    """
    provinces = sorted(validator.get_provinces())
    return {
        "provinces": provinces,
        "count": len(provinces),
    }


@router.get("/districts/regions", response_model=dict)
def get_regions(
    validator: Annotated[FilterValidator, Depends(get_filter_validator)],
):
    """
    Get all valid region values.

    **Use this to:** Discover valid region filter values before querying.

    **Response:**
    ```json
    {
        "regions": ["Hill", "Mountain", "Tarai", ...],
        "count": 3
    }
    ```
    """
    regions = sorted(validator.get_regions())
    return {
        "regions": regions,
        "count": len(regions),
    }


@router.get("/districts/search", response_model=DistrictListResponse)
def search_districts(
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Search query (district name, substring match, case-insensitive)",
    ),
):
    """
    Search districts by name (substring, case-insensitive).

    **Query Parameters:**
    - `q`: Search query (minimum 1 character, maximum 100)

    **Response:**
    Returns districts where name contains query string (case-insensitive).

    **Examples:**
    ```
    GET /api/v1/districts/search?q=kathmandu
    GET /api/v1/districts/search?q=morang
    ```
    """
    # Sanitize for LIKE escape sequences
    pattern = q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    if not pattern:
        raise HTTPException(
            status_code=400, detail="Search query cannot be empty/whitespace"
        )

    # Case-insensitive substring search (uses index if available)
    stmt = (
        select(Districts)
        .where(Districts.name.ilike(f"%{pattern}%", escape="\\"))
        .order_by(Districts.name.asc())
    )

    results = db.execute(stmt).scalars().all()
    districts = [DistrictResponse.model_validate(d) for d in results]

    return DistrictListResponse(total=len(districts), districts=districts)


@router.get("/districts/{district_id}", response_model=DistrictResponse)
def get_district(
    district_id: int,
    db: Annotated[Session, Depends(get_db)],
    validator: Annotated[FilterValidator, Depends(get_filter_validator)],
):
    """
    Get a specific district by ID.

    **Path Parameters:**
    - `district_id`: District ID (1-77)

    **Response:**
    Returns district details including location, population, area.

    **Examples:**
    ```
    GET /api/v1/districts/1
    GET /api/v1/districts/15
    ```
    """
    if not validator.validate_district_id(district_id):
        raise HTTPException(
            status_code=404,
            detail=f"District {district_id} not found (valid range: 1-77)",
        )

    district = db.get(Districts, district_id)
    if not district:  # Sanity check (shouldn't happen if validator passed)
        raise HTTPException(status_code=404, detail=f"District {district_id} not found")

    return DistrictResponse.model_validate(district)
