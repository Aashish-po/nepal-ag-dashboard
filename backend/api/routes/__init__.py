"""
Backend router package for the Nepal Agricultural Intelligence Dashboard.

This module aggregates the FastAPI router objects used by the main
application, providing a single namespace for route definitions.

Example::

    from backend.api.routes import (
        districts_router,
        crops_router,
        yields_router,
        ...
    )
"""

from __future__ import annotations

from .climate import router as climate_router
from .commercialization import router as commercialization_router

# ---------------------------------------------------------------------------
# Domain routers (exported by feature modules)
# ---------------------------------------------------------------------------
from .correlation import router as correlation_router
from .crops import router as crops_router
from .districts import router as districts_router
from .export_crops import router as export_crops_router
from .exports import router as exports_router
from .forecasts import router as forecasts_router
from .yields import router as yields_router

__all__ = [
    "climate_router",
    "commercialization_router",
    "correlation_router",
    "crops_router",
    "districts_router",
    "export_crops_router",
    "exports_router",
    "forecasts_router",
    "yields_router",
]
