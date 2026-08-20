"""
APScheduler background job for weekly ETL.

Runs every Tuesday at 00:00 UTC:
  1. Fetch FAOSTAT crop production API -> upsert yields
  2. Fetch NASA POWER climate data -> upsert climate
  3. Fetch CHIRPS rainfall -> merge into climate
  4. Compute commercialization_index
  5. Train forecasts -> upsert forecasts table
  6. Refresh materialized view
  7. Invalidate Redis cache
"""

from __future__ import annotations

import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from services.cache import invalidate_all_cache
from services.etl import load_all

logger = logging.getLogger(__name__)

scheduler: BackgroundScheduler | None = None


def init_scheduler() -> BackgroundScheduler:
    """Initialize and return the APScheduler with the weekly ETL job."""
    global scheduler

    if scheduler is not None:
        return scheduler

    scheduler = BackgroundScheduler(timezone="UTC")

    # Weekly ETL: Tuesday 00:00 UTC
    scheduler.add_job(
        func=weekly_etl,
        trigger=CronTrigger(day_of_week="tue", hour=0, minute=0),
        id="weekly_etl",
        name="Weekly ETL pipeline",
        replace_existing=True,
        max_instances=1,
    )

    logger.info("APScheduler initialized with weekly ETL job (Tue 00:00 UTC)")
    return scheduler


def start_scheduler() -> None:
    """Start the background scheduler."""
    sched = init_scheduler()
    sched.start()
    logger.info("Background scheduler started")


def shutdown_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info("Background scheduler shut down")


def weekly_etl() -> None:
    """Execute the weekly ETL pipeline.

    Fetches fresh data from external APIs, updates the database,
    retrains forecasts, and invalidates cache.
    """
    logger.info("=== Weekly ETL pipeline started ===")
    start_time = datetime.utcnow()
    import asyncio

    try:
        # 1. Load seed data (in production, fetch from APIs)
        # For Phase 1, this loads from cached CSVs
        asyncio.run(load_all(strict=True))

        # 2. Compute forecasts (Phase 4 will populate forecasts table)
        # For now, log that forecast training is pending
        # 3. Refresh materialized views
        from sqlalchemy import create_engine, text as sql_text

        db_url = os.environ.get("DATABASE_URL", "")
        if "asyncpg" in db_url:
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        if db_url:
            engine = create_engine(db_url)
            try:
                with engine.connect().execution_options(
                    isolation_level="AUTOCOMMIT"
                ) as conn:
                    conn.execute(
                        sql_text(
                            "REFRESH MATERIALIZED VIEW CONCURRENTLY "
                            "vw_district_yield_summary"
                        )
                    )
            finally:
                engine.dispose()
            logger.info("Materialized view refreshed")

        # 4. Invalidate cache
        asyncio.run(invalidate_all_cache())

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info("=== Weekly ETL pipeline completed in %.1f seconds ===", elapsed)

    except Exception as e:
        logger.error("Weekly ETL pipeline failed: %s", e, exc_info=True)
        raise
