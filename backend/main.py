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
from api.routes.yields import router as yields_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"backend","message":"%(message)s"}',
)
logger = logging.getLogger(__name__)

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
CORS_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()
]


app = FastAPI(
    title="Nepal Agricultural Intelligence Dashboard API",
    description="Real-time agricultural analytics API for Nepal districts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS: production must pin explicit origins (no wildcard); dev falls back to localhost.
if ENVIRONMENT == "production" and (not CORS_ORIGINS or "*" in CORS_ORIGINS):
    raise RuntimeError(
        "CORS_ORIGINS must be set to explicit origins (no wildcards) in production"
    )

allow_origins = CORS_ORIGINS or ["http://localhost:5173", "http://localhost:3000"]
allow_credentials = "*" not in allow_origins

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


# Root endpoint
@app.get("/")
def root():
    return {
        "service": "Nepal Agricultural Intelligence Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "districts": "/api/v1/districts",
            "crops": "/api/v1/crops",
            "yields": "/api/v1/yields/{district_id}/{crop_id}",
            "climate": "/api/v1/climate/{district_id}",
            "correlation": "/api/v1/correlation/{district_id}",
            "forecasts": "/api/v1/forecasts/{district_id}/{crop_id}",
        },
    }


# Health check endpoint
@app.get("/health")
def health():
    db_status = check_db_connection()
    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=db_status,
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))  # nosec B104 - bind all interfaces intentionally for container deploy
