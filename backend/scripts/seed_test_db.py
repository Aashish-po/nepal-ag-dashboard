"""Self-check: spin a fresh SQLite DB, create schema, seed, and assert
``main_export_countries`` round-trips as a list (not a pipe-delimited string).

Usage:
    python scripts/seed_test_db.py

Run from the ``backend/`` directory so ``from api...`` / ``from main...`` resolve.
"""

from __future__ import annotations

import asyncio
import os
import sys

# Ensure backend/ is the working root (api.db imports assume cwd == backend/).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_roundtrip.db")
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["ENVIRONMENT"] = "development"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


def seed() -> None:
    from api.db import init_db

    init_db()

    from services.etl import load_all

    results = asyncio.run(load_all(strict=False))
    assert results["export_crops"] > 0, (
        f"expected export_crops rows, got {results.get('export_crops')}"
    )
    assert results["commercialization_index"] > 0, "missing commercialization rows"
    print("seeded:", {k: v for k, v in results.items()})


def assert_export_countries_are_lists() -> None:
    from api.db import get_db
    from api.models.db_models import ExportCrops
    from sqlalchemy import select

    db = next(get_db())
    try:
        rows = db.execute(select(ExportCrops)).scalars().all()
        assert rows, "no export_crops rows"
        for r in rows:
            v = r.main_export_countries
            assert isinstance(v, list), (
                f"crop {r.crop_id} stored as {type(v).__name__}: {v!r}"
            )
            assert v, f"crop {r.crop_id} has empty list"
            # Every element must be a stripped, non-empty string (no stray pipes).
            for c in v:
                assert isinstance(c, str) and c.strip() == c and "|" not in c, (
                    f"crop {r.crop_id} country {c!r} looks un-split"
                )
        print("OK: all main_export_countries are clean lists")
    finally:
        db.close()


def assert_route_renders_clean() -> None:
    from api.db import get_db
    from api.routes.export_crops import get_export_crops

    db = next(get_db())
    try:
        resp = get_export_crops(district_id=1, db=db, year=2024)
        rendered = {
            c.crop_name: ", ".join(c.main_export_countries) for c in resp.export_crops
        }
        for crop, joined in rendered.items():
            # No bare pipe, no single-character-then-comma pattern.
            assert "|" not in joined, f"{crop}: raw pipe in {joined!r}"
            assert not any(len(part) == 1 for part in joined.split(", ")), (
                f"{crop}: char-split detected in {joined!r}"
            )
        print("OK: route renders joined strings cleanly:", rendered)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    assert_export_countries_are_lists()
    assert_route_renders_clean()
    # Release the SQLite connection before deleting the file.
    from api import db as _dbmod

    _dbmod._sync_engine.dispose()
    os.remove(DB_PATH)
    print("ALL CHECKS PASSED")
