"""
Nepal Agricultural Intelligence Dashboard — backend package.

This package hosts the FastAPI application, the database models, the API
routes and the long-running services (ETL, forecasting, scheduler, cache,
validators, climate helpers) that power the public read-only dashboard.

Typical entry point::

    uvicorn backend.main:app --reload
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Aashish Paudel"
__all__ = ["__author__", "__version__"]
