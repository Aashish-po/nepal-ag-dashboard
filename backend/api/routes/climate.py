from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from services.climate import compute_climate_summary
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db import get_db
from api.models.db_models import Districts
from api.models.schemas import ClimateRecord, ClimateResponse, ClimateSummary

router = APIRouter()


@router.get("/climate/{district_id}", response_model=ClimateResponse)
def get_climate(
    district_id: int,
    db: Session = Depends(get_db),
    date_start: str | None = Query(
        None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Start date (YYYY-MM)"
    ),
    date_end: str | None = Query(
        None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="End date (YYYY-MM)"
    ),
):
    district = db.get(Districts, district_id)
    if not district:
        raise HTTPException(
            status_code=404, detail=f"District with ID {district_id} not found"
        )

    conditions: list[str] = []
    params: dict = {"district_id": district_id}

    if date_start:
        conditions.append("observation_date >= :date_start")
        params["date_start"] = f"{date_start}-01"
    if date_end:
        year, month = (int(p) for p in date_end.split("-"))
        next_month = date(year + month // 12, month % 12 + 1, 1)
        conditions.append("observation_date < :date_end")
        params["date_end"] = next_month.isoformat()

    where_clause = " AND ".join(conditions)
    query = text(
        """
        SELECT observation_date, rainfall_mm, temperature_min_c,
               temperature_max_c, temperature_mean_c, solar_radiation_mj_m2,
               data_source
        FROM climate
        WHERE district_id = :district_id
        """
        + (f"  AND {where_clause}" if where_clause else "")
        + " ORDER BY observation_date"
    )

    results = db.execute(query, params).fetchall()

    climate_rows = []
    for row in results:
        climate_rows.append(
            {
                "district_id": district_id,
                "observation_date": str(row[0]) if row[0] else None,
                "rainfall_mm": float(row[1]) if row[1] is not None else None,
                "temperature_min_c": float(row[2]) if row[2] is not None else None,
                "temperature_max_c": float(row[3]) if row[3] is not None else None,
                "temperature_mean_c": float(row[4]) if row[4] is not None else None,
                "solar_radiation_mj_m2": float(row[5]) if row[5] is not None else None,
                "data_source": row[6],
            }
        )

    records = [ClimateRecord(**row) for row in climate_rows]
    summary_dict = compute_climate_summary(climate_rows)

    return ClimateResponse(
        district_id=district_id,
        district_name=district.name,
        data=records,
        summary=ClimateSummary(**summary_dict),
    )
