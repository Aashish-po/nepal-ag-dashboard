"""
FastAPI application entry point for the Nepal Agricultural Intelligence Dashboard.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from api.db import check_db_connection, init_db
from api.models.schemas import HealthResponse
from api.routes.climate import router as climate_router
from api.routes.commercialization import router as commercialization_router
from api.routes.correlation import router as correlation_router
from api.routes.crops import router as crops_router
from api.routes.districts import router as districts_router
from api.routes.export_crops import router as export_crops_router
from api.routes.exports import router as exports_router
from api.routes.forecasts import router as forecasts_router
from api.routes.heatmap import router as heatmap_router
from api.routes.yields import router as yields_router
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"backend","message":"%(message)s"}',
)
logger = logging.getLogger(__name__)

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")

app = FastAPI(
    title="Nepal Agricultural Intelligence Dashboard API",
    description="Real-time agricultural analytics API for Nepal districts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS - require explicit origins, no wildcard with credentials
if CORS_ORIGINS and CORS_ORIGINS != [""]:
    allow_origins = [o.strip() for o in CORS_ORIGINS if o.strip()]
else:
    # Default to localhost for development
    allow_origins = ["http://localhost:5173", "http://localhost:3000"]

# Allow credentials when we have explicit origins (not wildcards) and origins are set
# This reflects the application's authentication requirement rather than just environment
allow_credentials = bool(allow_origins and "*" not in allow_origins)
# In production with credentials, require explicit origins and fail fast when misconfigured
if ENVIRONMENT == "production":
    if not allow_origins or allow_origins == [""] or "*" in allow_origins:
        raise RuntimeError(
            "CORS_ORIGINS must be set to explicit origins (no wildcards) in production "
            "when using credentials"
        )
    # Ensure we're using the configured origins in production
    allow_origins = [o.strip() for o in CORS_ORIGINS if o.strip()]
    if not allow_origins:
        raise RuntimeError(
            "CORS_ORIGINS must be set to non-empty explicit origins in production"
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize database tables in development (graceful: tests may mock the DB)
if ENVIRONMENT == "development":
    try:
        init_db()
    except SQLAlchemyError as exc:
        logger.warning("init_db skipped (no DB available): %s", exc)


@app.on_event("startup")
async def startup_event():
    logger.info("Application starting (environment: %s)", ENVIRONMENT)
    db_status = check_db_connection()
    if db_status == "connected":
        logger.info("Database connection established")
    else:
        logger.warning("Database connection failed — running in degraded mode")

    if ENVIRONMENT == "production":
        from services.scheduler import start_scheduler

        try:
            start_scheduler()
            logger.info("Background scheduler started")
        except SQLAlchemyError as exc:
            logger.error("Failed to start scheduler: %s", exc)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
    if ENVIRONMENT == "production":
        from services.scheduler import shutdown_scheduler

        shutdown_scheduler()


@app.get("/health")
def health():
    db_status = check_db_connection()
    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=db_status,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
    )


# Include all routers
app.include_router(districts_router, prefix="/api/v1")
app.include_router(crops_router, prefix="/api/v1")
app.include_router(yields_router, prefix="/api/v1")
app.include_router(climate_router, prefix="/api/v1")
app.include_router(correlation_router, prefix="/api/v1")
app.include_router(commercialization_router, prefix="/api/v1")
app.include_router(forecasts_router, prefix="/api/v1")
app.include_router(exports_router, prefix="/api/v1")
app.include_router(export_crops_router, prefix="/api/v1")
app.include_router(heatmap_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))  # nosec B104 - bind all interfaces intentionally for container deploy
