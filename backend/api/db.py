"""
Database session management for the Nepal Agricultural Intelligence Dashboard.

Provides a synchronous engine/session used by FastAPI routes, tests,
and the ETL pipeline.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from api.models.db_models import Base

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL", "postgresql://localhost:5432/nepal_ag_dev"
)

# Render provides postgres://; SQLAlchemy needs the postgresql:// scheme.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_sync_engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.environ.get("SQLALCHEMY_ECHO", "").lower() in ("true", "1"),
)

_SyncSessionLocal = sessionmaker(
    bind=_sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a synchronous database session."""
    db: Session = _SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (for local dev / testing)."""
    Base.metadata.create_all(bind=_sync_engine)
    logger.info("Database tables created via init_db()")


def check_db_connection() -> str:
    """Return 'connected' if the database is reachable, otherwise 'error'."""
    try:
        with _sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "connected"
    except Exception as exc:  # noqa: BLE001
        logger.error("Database connection failed: %s", exc)
        return "error"
