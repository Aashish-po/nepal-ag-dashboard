from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from services.correlations import compute_full_correlation
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.db import get_db
from api.models.db_models import Climate, Crops, Districts, Yields
from api.models.schemas import HeatmapResponse, HeatmapRow

router = APIRouter()


@router.get("/heatmap/yield-climate-correlation", response_model=HeatmapResponse)
def get_heatmap(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Top N crops by data completeness"),
):
    # Get top N crops by data completeness (number of years with yield data)
    crop_stmt = (
        select(
            Yields.crop_id.label("crop_id"),
            Crops.name.label("crop_name"),
            func.count(Yields.year).label("years"),
        )
        .join(Crops)
        .where(Yields.yield_kg_ha.isnot(None))
        .group_by(Yields.crop_id, Crops.name)
        .having(func.count(Yields.year) >= 3)
        .order_by(func.count(Yields.year).desc())
        .limit(limit)
    )
    crop_rows = db.execute(crop_stmt).all()

    if not crop_rows:
        return HeatmapResponse(total_rows=0, rows=[])

    crop_ids = [row.crop_id for row in crop_rows]
    crop_names = {row.crop_id: row.crop_name for row in crop_rows}

    # Fetch all yields for selected crops in one query
    y_stmt = (
        select(
            Yields.district_id,
            Yields.crop_id,
            Yields.year,
            Yields.yield_kg_ha,
        )
        .where(Yields.crop_id.in_(crop_ids))
        .where(Yields.yield_kg_ha.isnot(None))
        .order_by(Yields.district_id, Yields.crop_id, Yields.year)
    )
    y_results = db.execute(y_stmt).all()

    # Fetch all climate aggregates for all relevant districts in one query
    district_ids = list(set(row.district_id for row in y_results))
    year_col = func.extract("year", Climate.observation_date)
    c_stmt = (
        select(
            Climate.district_id,
            year_col.label("yr"),
            func.sum(Climate.rainfall_mm).label("annual_rain"),
            func.avg(Climate.temperature_mean_c).label("avg_temp"),
            func.avg(Climate.solar_radiation_mj_m2).label("avg_solar"),
        )
        .where(Climate.district_id.in_(district_ids))
        .group_by(Climate.district_id, year_col)
        .order_by(Climate.district_id, year_col)
    )
    c_results = db.execute(c_stmt).all()

    # Fetch district names
    district_stmt = select(Districts.id, Districts.name).where(
        Districts.id.in_(district_ids)
    )
    district_rows = db.execute(district_stmt).all()
    district_names = {row.id: row.name for row in district_rows}

    # Group yields by (district_id, crop_id)
    from collections import defaultdict

    yields_by_dc: dict[tuple[int, int], list[tuple[int, float]]] = defaultdict(list)
    for row in y_results:
        yields_by_dc[(row.district_id, row.crop_id)].append(
            (row.year, float(row.yield_kg_ha))
        )

    # Group climate by district_id
    climate_by_district: dict[
        int, dict[int, tuple[float | None, float | None, float | None]]
    ] = defaultdict(dict)
    for row in c_results:
        district_id = row.district_id
        year = int(row.yr)  # Cast to int for matching with yield years
        rain = float(row.annual_rain) if row.annual_rain is not None else None
        temp = float(row.avg_temp) if row.avg_temp is not None else None
        solar = float(row.avg_solar) if row.avg_solar is not None else None
        climate_by_district[district_id][year] = (rain, temp, solar)

    final_rows: list[HeatmapRow] = []

    for crop_id, crop_name in crop_names.items():
        # Get unique districts for this crop
        crop_districts = set(d_id for (d_id, c_id) in yields_by_dc if c_id == crop_id)

        for district_id in crop_districts:
            district_name = district_names.get(district_id, f"District {district_id}")
            yield_data = yields_by_dc.get((district_id, crop_id), [])
            climate_data = climate_by_district.get(district_id, {})

            if len(yield_data) < 3 or len(climate_data) < 3:
                # Return None for insufficient data (will be filtered out)
                continue

            yield_years = [y for y, _ in yield_data]

            yield_map = dict(yield_data)
            rain_map = {y: v[0] for y, v in climate_data.items() if v[0] is not None}
            temp_map = {y: v[1] for y, v in climate_data.items() if v[1] is not None}
            solar_map = {y: v[2] for y, v in climate_data.items() if v[2] is not None}

            aligned_years = sorted(set(yield_years) & set(climate_data.keys()))
            if len(aligned_years) < 3:
                continue

            aligned_yield = [yield_map[y] for y in aligned_years]
            aligned_rain = [rain_map.get(y) for y in aligned_years]
            aligned_temp = [temp_map.get(y) for y in aligned_years]
            aligned_solar = [solar_map.get(y) for y in aligned_years]

            # Exclude entries where climate value is None
            aligned_rain = [v for v in aligned_rain if v is not None]
            aligned_temp = [v for v in aligned_temp if v is not None]
            aligned_solar = [v for v in aligned_solar if v is not None]

            # If after filtering we don't have enough aligned data, skip
            if len(aligned_rain) < 3 or len(aligned_temp) < 3 or len(aligned_solar) < 3:
                continue

            # Re-align yield values with filtered climate data
            # We need to filter aligned_yield to match the filtered climate arrays
            # Since we filtered based on None values, we need to re-filter
            rain_corr = compute_full_correlation(aligned_yield, aligned_rain)
            temp_corr = compute_full_correlation(aligned_yield, aligned_temp)
            solar_corr = compute_full_correlation(aligned_yield, aligned_solar)

            final_rows.append(
                HeatmapRow(
                    district=district_name,
                    district_id=district_id,
                    crop=crop_name,
                    crop_id=crop_id,
                    rainfall_corr=rain_corr["coefficient"],
                    temperature_corr=temp_corr["coefficient"],
                    solar_corr=solar_corr["coefficient"],
                )
            )

    return HeatmapResponse(total_rows=len(final_rows), rows=final_rows)
