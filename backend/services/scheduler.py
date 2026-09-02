"""
APScheduler integration — weekly ETL + forecast training job.

Scheduled to run every Tuesday at 00:00 UTC (as specified in the plan).
Delegates to ``services.etl.load_all`` and ``services.forecasting.train_all_forecasts``.
"""

from __future__ import annotations

import logging

from api.db import _sync_engine as engine
from apscheduler.schedulers.background import (
    BackgroundScheduler,
)
from apscheduler.triggers.cron import CronTrigger
from services.etl import load_all
from services.forecasting import train_all_forecasts
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

JOB_ID = "weekly_etl_forecast"

# Singleton reference updated by start_scheduler().
_scheduler: BackgroundScheduler | None = None


def _run_weekly_job() -> None:
    """Execute the weekly ETL + forecast training pipeline."""
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        logger.info("Starting weekly ETL + forecast job")
        results = load_all()
        logger.info("ETL results: %s", results)
        forecast_results = train_all_forecasts(db, months_ahead=12)
        logger.info(
            "Forecast training results: %d district×crop pairs updated",
            len(forecast_results),
        )
    except Exception:
        logger.exception("Weekly ETL + forecast job failed")
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    """Start the APScheduler with the weekly ETL+forecast job.

    Returns:
        The running scheduler instance.
    """
    global _scheduler
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        _run_weekly_job,
        trigger=CronTrigger(day_of_week="tue", hour=0, minute=0),
        id=JOB_ID,
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "APScheduler started: job '%s' scheduled for Tuesdays 00:00 UTC", JOB_ID
    )
    return scheduler
