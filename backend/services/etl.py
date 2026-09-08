"""
ETL (Extract, Transform, Load) services for the Nepal Agricultural Intelligence Dashboard.

Handles:
  - Loading seed data from CSV files (districts, crops, yields, climate)
  - Validating data quality on ingestion
  - Upserting records into the database

Functions are designed to be called by the APScheduler weekly job
or the seed_db.py CLI script.
"""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Callable, Mapping
from typing import Any, cast

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = os.environ.get("DATA_DIR", "./data")


def validate_districts(df: pd.DataFrame) -> dict[str, list[str]]:
    """Validate districts.csv — previously skipped; now fails fast on 0/null population."""
    report: dict[str, list[str]] = {"errors": [], "warnings": []}
    if "population" in df.columns:
        pop = pd.to_numeric(df["population"], errors="coerce")
        bad = df[pop.isna() | (pop <= 0)]
        if len(bad) > 0:
            report["errors"].append(
                f"{len(bad)} rows with zero/null/non-numeric population"
            )
        tiny = df[(pop > 0) & (pop < 5000)]
        if len(tiny) > 0:
            report["warnings"].append(
                f"{len(tiny)} rows with population < 5,000 (implausible)"
            )
    if "area_sq_km" in df.columns:
        area = pd.to_numeric(df["area_sq_km"], errors="coerce")
        bad = df[area.isna() | (area <= 0)]
        if len(bad) > 0:
            report["errors"].append(
                f"{len(bad)} rows with zero/null/non-numeric area_sq_km"
            )
    if "id" in df.columns:
        dupes = int(df.duplicated(subset=["id"]).sum())
        if dupes > 0:
            report["errors"].append(f"{dupes} duplicate district id(s)")
        if len(df) != 77:
            report["warnings"].append(f"Expected 77 districts, got {len(df)}")
    logger.info(
        "District validation: %d errors, %d warnings",
        len(report["errors"]),
        len(report["warnings"]),
    )
    return report


# --------------------------------------------------------------------------- #
# Districts
# --------------------------------------------------------------------------- #


def load_districts_csv(filepath: str | None = None, strict: bool = False) -> int:
    """Load districts from CSV into the database.

    Args:
        filepath: Path to districts.csv. Defaults to data/districts.csv.
        strict: If True, raise on validation errors (e.g. zero population).

    Returns:
        Number of rows inserted.
    """
    filepath = filepath or os.path.join(DATA_DIR, "districts.csv")
    df = pd.read_csv(filepath)

    expected_cols = {
        "id",
        "name",
        "province",
        "region",
        "latitude",
        "longitude",
        "population",
        "area_sq_km",
    }
    if not expected_cols.issubset(df.columns):
        missing = expected_cols - set(df.columns)
        raise ValueError(f"districts.csv missing columns: {missing}")

    report = validate_districts(df)
    if report["errors"]:
        if strict:
            raise ValueError(f"District validation errors: {report['errors']}")
        logger.warning("District validation errors: %s", report["errors"][:5])
    if report["warnings"]:
        logger.warning("District validation warnings: %s", report["warnings"][:5])

    rows = df.to_dict("records")
    logger.info("Loading %d districts from %s", len(rows), filepath)
    return _upsert_table_rows("districts", rows, conflict_cols=["id"])


# --------------------------------------------------------------------------- #
# Crops
# --------------------------------------------------------------------------- #


def load_crops_csv(filepath: str | None = None) -> int:
    """Load crops reference data from CSV into the database."""
    filepath = filepath or os.path.join(DATA_DIR, "crops.csv")
    df = pd.read_csv(filepath)

    expected_cols = {
        "id",
        "name",
        "fao_code",
        "category",
        "unit",
        "is_export_crop",
        "is_subsistence",
    }
    if not expected_cols.issubset(df.columns):
        raise ValueError(
            f"crops.csv missing columns: {expected_cols - set(df.columns)}"
        )

    rows = df.to_dict("records")
    logger.info("Loading %d crops from %s", len(rows), filepath)
    return _upsert_table_rows("crops", rows, conflict_cols=["id"])


# --------------------------------------------------------------------------- #
# Yields (FAOSTAT)
# --------------------------------------------------------------------------- #


def load_yields_from_faostat(
    filepath: str | None = None,
    strict: bool = False,
    data: pd.DataFrame | None = None,
) -> int:
    """Parse FAOSTAT-style CSV, normalize, and upsert yield records.

    Expected CSV columns: district_id, crop_id, year, production_mt,
    area_harvested_ha, yield_kg_ha, data_source, data_quality

    Args:
        filepath: Path to FAOSTAT CSV file.
        strict: If True, raise ValueError when validation errors exist.

    Returns:
        Number of rows upserted.
    """
    filepath = filepath or os.path.join(DATA_DIR, "faostat_2014_2024.csv")
    df = data if data is not None else pd.read_csv(filepath)

    expected_cols = {
        "district_id",
        "crop_id",
        "year",
        "production_mt",
        "area_harvested_ha",
        "yield_kg_ha",
        "data_source",
        "data_quality",
    }
    if not expected_cols.issubset(df.columns):
        raise ValueError(
            f"FAOSTAT CSV missing columns: {expected_cols - set(df.columns)}"
        )

    # Validate data quality
    validation_report = validate_yields(df)
    if validation_report["errors"]:
        if strict:
            raise ValueError(f"Yield validation errors: {validation_report['errors']}")
        logger.warning("Yield validation errors: %s", validation_report["errors"][:5])

    rows = df.to_dict("records")
    logger.info("Loaded %d yield records from %s", len(rows), filepath)
    return _upsert_table_rows(
        "yields", rows, conflict_cols=["district_id", "crop_id", "year", "data_source"]
    )


# --------------------------------------------------------------------------- #
# Climate (CHIRPS + NASA POWER)
# --------------------------------------------------------------------------- #


def load_climate_from_chirps(
    filepath: str | None = None,
    strict: bool = False,
    data: pd.DataFrame | None = None,
) -> int:
    """Parse CHIRPS/NASA POWER-style CSV, normalize, and upsert climate records.

    Expected CSV columns: district_id, observation_date, rainfall_mm,
    temperature_min_c, temperature_max_c, temperature_mean_c,
    solar_radiation_mj_m2, data_source
    """
    filepath = filepath or os.path.join(DATA_DIR, "chirps_2014_2024.csv")
    df = data if data is not None else pd.read_csv(filepath)

    expected_cols = {
        "district_id",
        "observation_date",
        "rainfall_mm",
        "temperature_min_c",
        "temperature_max_c",
        "temperature_mean_c",
        "solar_radiation_mj_m2",
        "data_source",
    }
    if not expected_cols.issubset(df.columns):
        raise ValueError(
            f"Climate CSV missing columns: {expected_cols - set(df.columns)}"
        )

    validation_report = validate_climate(df)
    if validation_report["errors"]:
        if strict:
            raise ValueError(
                f"Climate validation errors: {validation_report['errors']}"
            )
        logger.warning("Climate validation errors: %s", validation_report["errors"][:5])

    rows = df.to_dict("records")
    logger.info("Loaded %d climate records from %s", len(rows), filepath)
    return _upsert_table_rows(
        "climate",
        rows,
        conflict_cols=["district_id", "observation_date", "data_source"],
    )


def load_export_crops(filepath: str | None = None) -> int:
    """Load export crops metadata from CSV."""
    filepath = filepath or os.path.join(DATA_DIR, "export_crops.csv")
    if not os.path.exists(filepath):
        logger.info("export_crops.csv not found, skipping")
        return 0

    df = pd.read_csv(filepath)
    rows = df.to_dict("records")
    logger.info("Loaded %d export crop records", len(rows))
    return _upsert_table_rows("export_crops", rows, conflict_cols=["crop_id"])


# --------------------------------------------------------------------------- #
# Commercialization index
# --------------------------------------------------------------------------- #


def compute_commercialization_index(
    seed_dir: str | None = None,
    strict: bool = False,
) -> int:
    """Compute the per-district commercialization index from yields and exports.

    Formula (matches the API route's ``components`` math):

        score = (export_crop_area_pct * 0.40)
              + (holding / 5.0 * 0.30)
              + (export_volume_ratio * 0.30)

    Each term is already in [0, 100]; the score is clipped to [0, 100] to
    keep the frontend's bar-chart domain sane.

    ``holding`` (avg holding size) is a coarse proxy from total cropped area:
    Nepal's median farm is ~0.5-1.5 ha, so we scale so the median district
    lands around 1.0 ha and clamp to a plausible [0.05, 10.0] range.

    Returns the number of rows upserted.
    """
    seed_dir = seed_dir or DATA_DIR
    yields_path = os.path.join(seed_dir, "faostat_2014_2024.csv")
    if not os.path.exists(yields_path):
        logger.warning("Yields CSV missing; skipping commercialization compute")
        return 0

    yields_df = pd.read_csv(yields_path)

    # Identify export crops from the crops table (single source of truth).
    from api.db import get_engine
    from api.models.db_models import Crops
    from sqlalchemy.orm import Session

    engine = get_engine()
    with Session(engine) as db:
        export_crop_ids = {
            int(c.id)
            for c in db.query(Crops).filter(Crops.is_export_crop.is_(True)).all()
        }

    if yields_df.empty or not export_crop_ids:
        logger.info("No yields or no export crops; skipping commercialization compute")
        return 0

    yields_df = yields_df.copy()
    yields_df["is_export"] = yields_df["crop_id"].isin(export_crop_ids)

    # Aggregate by (district_id, year).
    grouped = (
        yields_df.assign(
            _export_area=lambda d: d["area_harvested_ha"].where(d["is_export"], 0)
        )
        .assign(_export_prod=lambda d: d["production_mt"].where(d["is_export"], 0))
        .groupby(["district_id", "year"], dropna=False)
        .agg(
            total_area=("area_harvested_ha", "sum"),
            export_area=("_export_area", "sum"),
            total_production=("production_mt", "sum"),
            export_production=("_export_prod", "sum"),
        )
        .reset_index()
    )

    rows: list[dict[str, Any]] = []
    for _, r in grouped.iterrows():
        district_id = int(r["district_id"])
        year = int(r["year"])
        total_area = float(r["total_area"] or 0)
        export_area = float(r["export_area"] or 0)
        total_prod = float(r["total_production"] or 0)
        export_prod = float(r["export_production"] or 0)

        # % of cropped area that is export crops (clamped 0-100).
        export_crop_area_pct = (
            (export_area / total_area * 100.0) if total_area > 0 else 0.0
        )
        export_crop_area_pct = max(0.0, min(100.0, export_crop_area_pct))
        # Remaining area is treated as subsistence (Nepal's subsistence share
        # is ~60-80% of total — using 100% - export keeps the sum = 100).
        subsistence_area_pct = max(0.0, 100.0 - export_crop_area_pct)

        # Export volume ratio (clamped to 0-100).
        export_volume_ratio = (
            (export_prod / total_prod * 100.0) if total_prod > 0 else 0.0
        )
        export_volume_ratio = max(0.0, min(100.0, export_volume_ratio))

        # Holding-size proxy: total_area / 100_000 ha so the median district
        # maps to ~1.0 ha; clamp to a plausible Nepal range.
        avg_holding_size_ha = max(0.05, min(10.0, total_area / 100_000.0))

        # Score = weighted contributions, each term in 0-100. Clip at 100.
        holding_term = min(100.0, (avg_holding_size_ha / 5.0) * 100.0)
        score = (
            export_crop_area_pct * 0.40
            + holding_term * 0.30
            + export_volume_ratio * 0.30
        )
        score = round(max(0.0, min(100.0, score)), 2)

        rows.append(
            {
                "district_id": district_id,
                "year": year,
                "export_crop_area_pct": round(export_crop_area_pct, 2),
                "subsistence_area_pct": round(subsistence_area_pct, 2),
                "avg_holding_size_ha": round(avg_holding_size_ha, 2),
                "export_volume_ratio": round(export_volume_ratio, 2),
                "commercialization_score": score,
            }
        )

    logger.info("Computed %d commercialization_index rows", len(rows))
    return _upsert_table_rows(
        "commercialization_index", rows, conflict_cols=["district_id", "year"]
    )


# --------------------------------------------------------------------------- #
# Data validation
# --------------------------------------------------------------------------- #


def validate_yields(df: pd.DataFrame) -> dict[str, list[str]]:
    """Validate yield data for quality issues."""
    report: dict[str, list[str]] = {"errors": [], "warnings": []}

    if "production_mt" in df.columns:
        bad = df[df["production_mt"] < 0]
        if len(bad) > 0:
            report["errors"].append(f"{len(bad)} rows with negative production_mt")

    if "area_harvested_ha" in df.columns:
        bad = df[df["area_harvested_ha"] <= 0]
        if len(bad) > 0:
            report["errors"].append(
                f"{len(bad)} rows with zero or negative area_harvested_ha"
            )

    if all(
        c in df.columns for c in ["production_mt", "area_harvested_ha", "yield_kg_ha"]
    ):
        df_copy = df.copy()
        df_copy = df_copy[df_copy["area_harvested_ha"] > 0]
        df_copy["computed_yield"] = (df_copy["production_mt"] * 1000) / df_copy[
            "area_harvested_ha"
        ]
        mismatch = int(
            (abs(df_copy["computed_yield"] - df_copy["yield_kg_ha"]) > 0.1).sum()
        )
        if mismatch > 0:
            report["warnings"].append(
                f"{mismatch} rows where yield_kg_ha differs from computed value"
            )

    if "year" in df.columns:
        from api.models.db_models import (
            MAX_SUPPORTED_HARVEST_YEAR,
            MIN_SUPPORTED_HARVEST_YEAR,
        )

        valid_years = df[
            (df["year"] >= MIN_SUPPORTED_HARVEST_YEAR)
            & (df["year"] <= MAX_SUPPORTED_HARVEST_YEAR)
        ]
        invalid = len(df) - len(valid_years)
        if invalid > 0:
            report["errors"].append(
                f"{invalid} rows with year outside "
                f"{MIN_SUPPORTED_HARVEST_YEAR}-{MAX_SUPPORTED_HARVEST_YEAR}"
            )

    dupe_keys = ["district_id", "crop_id", "year", "data_source"]
    if all(c in df.columns for c in dupe_keys):
        dupes = int(df.duplicated(subset=dupe_keys).sum())
        if dupes > 0:
            report["warnings"].append(f"{dupes} duplicate rows detected")

    logger.info(
        "Yield validation: %d errors, %d warnings",
        len(report["errors"]),
        len(report["warnings"]),
    )
    return report


def validate_climate(df: pd.DataFrame) -> dict[str, list[str]]:
    """Validate climate data for quality issues."""
    report: dict[str, list[str]] = {"errors": [], "warnings": []}

    if "rainfall_mm" in df.columns:
        bad = df[df["rainfall_mm"] < 0]
        if len(bad) > 0:
            report["errors"].append(f"{len(bad)} rows with negative rainfall")

    temp_cols = ["temperature_min_c", "temperature_max_c"]
    if all(c in df.columns for c in temp_cols):
        bad = df[df[temp_cols[0]] >= df[temp_cols[1]]]
        if len(bad) > 0:
            report["errors"].append(f"{len(bad)} rows where min >= max temperature")

    # Check date range
    if "observation_date" in df.columns:
        valid_dates = pd.to_datetime(df["observation_date"], errors="coerce")
        invalid = valid_dates.isna().sum()
        if invalid > 0:
            report["errors"].append(f"{invalid} rows with invalid observation_date")

    logger.info(
        "Climate validation: %d errors, %d warnings",
        len(report["errors"]),
        len(report["warnings"]),
    )
    return report


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _upsert_table_rows(
    table_name: str, rows: list[dict], conflict_cols: list[str]
) -> int:
    """Bulk upsert rows into a table using dialect-specific INSERT ... ON CONFLICT."""
    from api.models.db_models import MISSING_DATA_SOURCE, Base
    from sqlalchemy import Date, DateTime, create_engine
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert

    # .strip(): a trailing newline from a pasted URL would corrupt the DB name.
    db_url = os.environ.get(
        "DATABASE_URL", "postgresql://localhost:5432/nepal_ag_dev"
    ).strip()
    # Convert async URL to sync URL for pandas/pyodbc
    if "postgresql+asyncpg" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    engine = create_engine(db_url)

    try:
        if not rows:
            return 0

        table = Base.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Unknown ETL table: {table_name}")

        for row in rows:
            for column in ("data_source", "forecast_model"):
                if column in row and (row[column] is None or pd.isna(row[column])):
                    row[column] = MISSING_DATA_SOURCE
        df = pd.DataFrame(rows).astype(object)

        # SQLite's Date/DateTime bind processors reject strings (Postgres
        # coerces them); convert CSV string values for date-typed columns so
        # both dialects get real date/datetime objects.
        for col in df.columns:
            sa_col = table.columns.get(col)
            if sa_col is None:
                continue
            if isinstance(sa_col.type, DateTime):
                df[col] = pd.to_datetime(df[col], errors="coerce")
            elif isinstance(sa_col.type, Date):
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

        df = df.where(pd.notna(df), None)

        invalid_columns = set(df.columns) - set(table.columns.keys())
        if invalid_columns:
            raise ValueError(
                f"Unknown columns for {table_name}: {sorted(invalid_columns)}"
            )
        records = cast(list[Mapping[str, Any]], df.to_dict("records"))

        invalid_conflicts = set(conflict_cols) - set(table.columns.keys())
        if invalid_conflicts:
            raise ValueError(
                f"Unknown conflict columns for {table_name}: {sorted(invalid_conflicts)}"
            )

        # Select dialect-specific insert constructor
        dialect_name = engine.dialect.name
        insert_factory: Callable[[Any], Any]
        if dialect_name == "sqlite":
            insert_factory = sqlite_insert
        else:
            insert_factory = pg_insert

        # Determine batch size based on dialect (SQLite has ~999 variable limit)
        is_sqlite = dialect_name == "sqlite"
        num_cols = len(df.columns)
        if is_sqlite:
            batch_size = max(1, 999 // num_cols)
        else:
            batch_size = 100

        with engine.connect() as conn:
            logger.info("Upserting %d rows into %s", len(df), table_name)
            for i in range(0, len(records), batch_size):
                batch = records[i : i + batch_size]
                batch_stmt = insert_factory(table).values(batch)
                final_update_cols = {
                    column: getattr(batch_stmt.excluded, column)  # type: ignore[attr-defined]
                    for column in df.columns
                    if column not in conflict_cols
                }
                batch_full_stmt = (
                    batch_stmt.on_conflict_do_update(  # type: ignore[attr-defined]
                        index_elements=conflict_cols,
                        set_=final_update_cols,
                    )
                    if final_update_cols
                    else batch_stmt.on_conflict_do_nothing(index_elements=conflict_cols)  # type: ignore[attr-defined]
                )
                conn.execute(batch_full_stmt)
            conn.commit()
    finally:
        engine.dispose()

    return len(rows)


async def load_all(seed_dir: str | None = None, strict: bool = False) -> dict[str, int]:
    """Load all seed data in the correct order.

    Order: districts → crops → yields → climate → export_crops → commercialization_index

    Args:
        seed_dir: Directory containing seed data CSV files.
        strict: If True, raise ValueError when validation errors exist.

    Returns:
        Dict mapping each step name to the number of rows loaded.
    """
    seed_dir = seed_dir or DATA_DIR

    results: dict[str, int] = {}

    # 1. Districts
    results["districts"] = await asyncio.to_thread(
        load_districts_csv, os.path.join(seed_dir, "districts.csv"), strict
    )

    # 2. Crops
    results["crops"] = await asyncio.to_thread(
        load_crops_csv, os.path.join(seed_dir, "crops.csv")
    )

    # 3. Yields (loader reads + validates; raises on strict when errors exist)
    results["yields"] = await asyncio.to_thread(
        load_yields_from_faostat,
        os.path.join(seed_dir, "faostat_2014_2024.csv"),
        strict,
    )

    # 4. Climate (loader reads + validates; raises on strict when errors exist)
    results["climate"] = await asyncio.to_thread(
        load_climate_from_chirps,
        os.path.join(seed_dir, "chirps_2014_2024.csv"),
        strict,
    )

    # 5. Export crops
    results["export_crops"] = await asyncio.to_thread(
        load_export_crops, os.path.join(seed_dir, "export_crops.csv")
    )

    # 6. Commercialization index (derived from yields + export_crops).
    # ponytail: runs after export_crops because export_crop_ids comes from the
    # crops table populated earlier; runs after yields because the input
    # aggregates over faostat_2014_2024.csv.
    results["commercialization_index"] = await asyncio.to_thread(
        compute_commercialization_index, seed_dir, strict
    )

    logger.info("All seed data loaded successfully")
    return results
