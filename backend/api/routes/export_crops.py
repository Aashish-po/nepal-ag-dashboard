from typing import Annotated

from api.db import get_db
from api.models.db_models import (
    MAX_SUPPORTED_HARVEST_YEAR,
    MIN_SUPPORTED_HARVEST_YEAR,
    Crops,
    Districts,
    ExportCrops,
    Yields,
)
from api.models.schemas import ExportCropInfo, ExportCropsResponse, ExportSeason
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter()


def _export_crop_info(
    *,
    crop_id: int,
    crop_name: str,
    production_mt: float | None,
    area_harvested_ha: float | None,
    yield_kg_ha: float | None,
    avg_price_usd_per_mt: float | None,
    main_export_countries: list[str] | str | None,
    season_start_month: int | None,
    season_end_month: int | None,
    notes: str | None,
) -> ExportCropInfo:
    """Assemble one export-crop row, computing estimated revenue.

    Revenue is production x price when both are known, else ``None``.
    """
    # ponytail: normalize legacy data. Older seeds stored this as a raw
    # pipe-delimited string ("India|Japan") in a non-JSON SQLite column;
    # joining such a string char-by-char produces "I, n, d, i, a". Coerce
    # both shapes (list or pipe-string) here so every caller is protected.
    # Remove once all deployments re-seed with the JSON-column ETL.
    if isinstance(main_export_countries, str):
        countries = [c.strip() for c in main_export_countries.split("|") if c.strip()]
    elif isinstance(main_export_countries, list):
        countries = [str(c).strip() for c in main_export_countries if str(c).strip()]
    else:
        countries = []
    revenue = (
        production_mt * avg_price_usd_per_mt
        if production_mt is not None and avg_price_usd_per_mt is not None
        else None
    )
    season = (
        ExportSeason(start_month=season_start_month, end_month=season_end_month)
        if season_start_month is not None and season_end_month is not None
        else None
    )
    return ExportCropInfo(
        crop_id=crop_id,
        crop_name=crop_name,
        production_mt=production_mt,
        area_harvested_ha=area_harvested_ha,
        yield_kg_ha=yield_kg_ha,
        export_potential_mt=production_mt,
        avg_price_usd_per_mt=avg_price_usd_per_mt,
        estimated_revenue_usd=revenue,
        export_season=season,
        main_export_countries=countries,
        notes=notes,
    )


@router.get("/export-crops/{district_id}", response_model=ExportCropsResponse)
def get_export_crops(
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

    stmt = (
        select(Yields, Crops, ExportCrops)
        .join(Crops, Yields.crop_id == Crops.id)
        .outerjoin(ExportCrops, ExportCrops.crop_id == Crops.id)
        .where(Yields.district_id == district_id)
        .where(Yields.year == year)
        .where(Crops.is_export_crop.is_(True))
        .order_by(Crops.name)
    )

    crops = [
        _export_crop_info(
            crop_id=c.id,
            crop_name=c.name,
            production_mt=(
                float(y.production_mt) if y.production_mt is not None else None
            ),
            area_harvested_ha=(
                float(y.area_harvested_ha) if y.area_harvested_ha is not None else None
            ),
            yield_kg_ha=float(y.yield_kg_ha) if y.yield_kg_ha is not None else None,
            avg_price_usd_per_mt=(
                float(ec.avg_price_usd_per_mt)
                if ec is not None and ec.avg_price_usd_per_mt is not None
                else None
            ),
            main_export_countries=ec.main_export_countries if ec is not None else None,
            season_start_month=ec.export_season_start_month if ec is not None else None,
            season_end_month=ec.export_season_end_month if ec is not None else None,
            notes=ec.notes if ec is not None else None,
        )
        for y, c, ec in db.execute(stmt).all()
    ]

    revenues = [
        ci.estimated_revenue_usd for ci in crops if ci.estimated_revenue_usd is not None
    ]

    return ExportCropsResponse(
        district_id=district_id,
        district_name=district.name,
        year=year,
        export_crops=crops,
        total_export_revenue_usd=sum(revenues) if revenues else None,
    )
