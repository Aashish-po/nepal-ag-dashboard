from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from services.correlations import calculate_yield_statistics
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.db import get_db
from api.models.db_models import Crops, Districts, Forecasts, Yields
from api.models.schemas import ForecastMonth, ForecastResponse, ModelDiagnostics

router = APIRouter()


def _f(value) -> float | None:
    return float(value) if value is not None else None


def _recommendation(trend: str | None, forecasts: list[ForecastMonth]) -> str:
    if not forecasts:
        return "No forecast data available"
    if trend == "INCREASING":
        return "Growth trend expected; consider expanding cultivation area"
    if trend == "DECREASING":
        return "Risk of decline; consider drought-resistant varieties"
    return "Stable yield expected; monitor climate conditions"


@router.get("/forecasts/{district_id}/{crop_id}", response_model=ForecastResponse)
def get_forecasts(
    district_id: int,
    crop_id: int,
    db: Annotated[Session, Depends(get_db)],
    months_ahead: int = Query(12, ge=1, le=36),
):
    district = db.get(Districts, district_id)
    if not district:
        raise HTTPException(
            status_code=404, detail=f"District with ID {district_id} not found"
        )

    crop = db.get(Crops, crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop with ID {crop_id} not found")

    historical_stmt = (
        select(Yields)
        .where(Yields.district_id == district_id)
        .where(Yields.crop_id == crop_id)
        .where(Yields.yield_kg_ha.isnot(None))
        .order_by(Yields.year)
    )
    historical = db.execute(historical_stmt).scalars().all()
    years_of_data = len({int(row.year) for row in historical})

    if years_of_data < 5:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Forecast requires >= 5 years of historical data. "
                f"Only {years_of_data} year(s) available for {crop.name} in {district.name}."
            ),
        )

    # Get the latest forecast for each month (by forecast_date) and filter to future months
    # First, get the latest forecast_date per forecast_month
    latest_forecast_subq = (
        select(
            Forecasts.forecast_month,
            func.max(Forecasts.forecast_date).label("latest_forecast_date"),
        )
        .where(Forecasts.district_id == district_id)
        .where(Forecasts.crop_id == crop_id)
        .group_by(Forecasts.forecast_month)
        .subquery()
    )

    # Join back to get full forecast records for the latest forecast_date per month
    from datetime import date, datetime, timezone

    now = datetime.now(tz=timezone.utc)
    current_month_start = date(now.year, now.month, 1)
    forecast_stmt = (
        select(Forecasts)
        .join(
            latest_forecast_subq,
            (Forecasts.forecast_month == latest_forecast_subq.c.forecast_month)
            & (Forecasts.forecast_date == latest_forecast_subq.c.latest_forecast_date)
            & (Forecasts.district_id == district_id)
            & (Forecasts.crop_id == crop_id),
        )
        .where(Forecasts.forecast_month >= current_month_start)
        .order_by(Forecasts.forecast_month)
    )
    results = db.execute(forecast_stmt).scalars().all()

    months = months_ahead
    forecasts_list = [
        ForecastMonth(
            forecast_month=str(r.forecast_month),
            forecast_yield_kg_ha=_f(r.forecast_yield_kg_ha),
            lower_ci_95=_f(r.lower_ci_95),
            upper_ci_95=_f(r.upper_ci_95),
            forecast_model=r.forecast_model,
            forecast_date=str(r.forecast_date) if r.forecast_date else None,
        )
        for r in results[:months]
    ]

    first = results[0] if results else None
    model_name = first.forecast_model if first else None
    rmse = _f(first.rmse_kg_ha) if first else None
    mae = _f(first.mae_kg_ha) if first else None
    mape = _f(first.mape_pct) if first else None

    # Calculate statistics from historical data for recommendation
    stats = calculate_yield_statistics(historical)

    recommendation = _recommendation(stats.get("trend"), forecasts_list)

    return ForecastResponse(
        district_id=district_id,
        district_name=district.name,
        crop_id=crop_id,
        crop_name=crop.name,
        forecast_horizon_months=months_ahead,
        forecast_model=model_name,
        model_diagnostics=ModelDiagnostics(
            rmse_kg_ha=rmse, mae_kg_ha=mae, mape_pct=mape
        ),
        forecasts=forecasts_list,
        recommendation=recommendation,
    )
