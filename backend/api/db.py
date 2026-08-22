"""
Database session management for the Nepal Agricultural Intelligence Dashboard.

Provides both a synchronous engine (for FastAPI routes and TestClient)
and an asynchronous engine (for async routes), plus utilities for the ETL pipeline.
"""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from api.models.db_models import Base

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL", "postgresql://localhost:5432/nepal_ag_dev"
)

# Normalize scheme: support postgresql://, postgres://, and sqlite://
# Also recognize driver-qualified schemes like postgresql+psycopg://, postgresql+asyncpg://, mysql+pymysql://
_normalized_db_url: str = DATABASE_URL
if _normalized_db_url.startswith("postgres://"):
    _normalized_db_url = _normalized_db_url.replace("postgres://", "postgresql://", 1)
elif (
    _normalized_db_url.startswith("postgresql://")
    or "+" in _normalized_db_url.split("://")[0]
):
    # Already normalized or driver-qualified (e.g., postgresql+psycopg://)
    pass
elif _normalized_db_url.startswith("sqlite://"):
    pass
else:
    # Default to postgresql if no recognized scheme
    _normalized_db_url = f"postgresql://{_normalized_db_url}"

DATABASE_URL = _normalized_db_url

# Convert to async URL if using postgresql (asyncpg)
# SQLite is sync-only
ASYNC_DATABASE_URL: str | None = None
if _normalized_db_url.startswith("postgresql://"):
    ASYNC_DATABASE_URL = _normalized_db_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
elif "+" in _normalized_db_url.split("://")[0] and _normalized_db_url.split("://")[
    0
].startswith("postgresql"):
    # Already has a driver, replace with asyncpg driver if it's a postgresql variant
    base_scheme = _normalized_db_url.split("://")[0]
    if base_scheme.startswith("postgresql+"):
        # Replace the driver part with asyncpg
        ASYNC_DATABASE_URL = _normalized_db_url.replace(
            base_scheme, "postgresql+asyncpg", 1
        )
    else:
        ASYNC_DATABASE_URL = None
else:
    ASYNC_DATABASE_URL = None

# ---------------------------------------------------------------------------
# Synchronous engine (used by API routes and tests)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Asynchronous engine (used by async routes) - lazily created
# ---------------------------------------------------------------------------

_async_engine = None
_AsyncSessionLocal = None

if ASYNC_DATABASE_URL:
    _async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.environ.get("SQLALCHEMY_ECHO", "").lower() in ("true", "1"),
    )

    _AsyncSessionLocal = async_sessionmaker(
        bind=_async_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a synchronous database session."""
    db: Session = _SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an asynchronous database session."""
    if _AsyncSessionLocal is None:
        raise RuntimeError(
            "Async database engine not available. "
            "Async operations require a PostgreSQL database URL (postgresql:// or postgres://). "
            "SQLite is not supported for async operations."
        )
    async with _AsyncSessionLocal() as db:
        yield db


def get_sync_engine():
    """Return the synchronous engine (used by ETL for bulk inserts)."""
    return _sync_engine


def get_async_engine():
    """Return the asynchronous engine if available, else None."""
    return _async_engine


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
    except Exception as exc:
        logger.error("Database connection failed: %s", exc)
        return "error"


__all__ = [
    "ASYNC_DATABASE_URL",
    "DATABASE_URL",
    "Base",
    "_AsyncSessionLocal",
    "_SyncSessionLocal",
    "_async_engine",
    "_sync_engine",
    "check_db_connection",
    "get_async_db",
    "get_async_engine",
    "get_db",
    "get_sync_engine",
    "init_db",
]
