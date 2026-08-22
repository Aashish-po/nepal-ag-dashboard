"""
CLI script to load seed data into the database.

Usage:
    python -m scripts.seed_db --load-all
    python -m scripts.seed_db --generate-data  # Generate synthetic data CSVs first
    python -m scripts.seed_db --load-all --strict
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

# Ensure backend directory is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.db import check_db_connection, init_db
from services.etl import load_all

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DATA_DIR = os.environ.get(
    "DATA_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
)


def generate_synthetic_data():
    """Generate synthetic but realistic Nepal agricultural data.

    Populates faostat_2014_2024.csv and chirps_2014_2024.csv with realistic
    values based on the data dictionary in plans/09_DATA_DICTIONARY.md.
    """
    import csv
    import random

    random.seed(42)

    # Load districts and crops
    import pandas as pd

    districts = pd.read_csv(os.path.join(DATA_DIR, "districts.csv"))
    crops = pd.read_csv(os.path.join(DATA_DIR, "crops.csv"))

    # Yield ranges by category (from data dictionary)
    category_ranges = {
        "Cereal": (1500, 4000),
        "Legume": (800, 1500),
        "Vegetable": (5000, 20000),
        "Fruit": (2000, 10000),
        "Oilseed": (1000, 3000),
        "Spice": (500, 1500),  # Cardamom is lower area but higher value
        "Export": (1500, 5000),
        "Cash": (50000, 100000),  # Sugarcane
    }

    # Generate yields
    yield_rows = []
    for _, district in districts.iterrows():
        for _, crop in crops.iterrows():
            category = crop["category"]
            if category in category_ranges:
                lo, hi = category_ranges[category]
            else:
                lo, hi = 1500, 4000

            for year in range(2014, 2025):
                # Add trend and noise
                base_yield = (lo + hi) / 2
                trend = random.uniform(-10, 15) * (year - 2014)  # Growing trend
                noise = random.gauss(0, (hi - lo) * 0.15)
                yield_val = max(lo * 0.5, min(hi * 1.5, base_yield + trend + noise))

                area = random.uniform(50000, 500000)
                production = (yield_val * area) / 1000

                yield_rows.append(
                    {
                        "district_id": int(district["id"]),
                        "crop_id": int(crop["id"]),
                        "year": year,
                        "production_mt": round(production, 2),
                        "area_harvested_ha": round(area, 2),
                        "yield_kg_ha": round(yield_val, 2),
                        "data_source": "FAOSTAT",
                        "data_quality": (
                            "Official" if random.random() > 0.2 else "Estimated"
                        ),
                    }
                )

    yields_path = os.path.join(DATA_DIR, "faostat_2014_2024.csv")
    with open(yields_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "district_id",
                "crop_id",
                "year",
                "production_mt",
                "area_harvested_ha",
                "yield_kg_ha",
                "data_source",
                "data_quality",
            ],
        )
        writer.writeheader()
        writer.writerows(yield_rows)
    logger.info("Generated %d yield records → %s", len(yield_rows), yields_path)

    # Generate climate data
    climate_rows = []
    for _, district in districts.iterrows():
        district["latitude"]
        district["longitude"]
        # Approximate climate based on region
        region = district["region"]
        if region == "Mountain":
            base_temp = 8
            base_rain = 800
            solar_factor = 1.0
        elif region == "Hill":
            base_temp = 18
            base_rain = 1600
            solar_factor = 0.9
        else:  # Terai
            base_temp = 22
            base_rain = 1400
            solar_factor = 1.1

        for year in range(2014, 2025):
            for month in range(1, 13):
                # Monthly patterns
                if 6 <= month <= 9:  # Monsoon
                    rain = base_rain * 0.4 * random.uniform(0.8, 1.2)
                    temp = base_temp + random.uniform(-2, 3)
                else:  # Dry season
                    rain = base_rain * 0.1 * random.uniform(0.5, 1.5)
                    temp = base_temp - abs(month - 1) * 0.8 + random.uniform(-3, 2)

                rainfall = max(0, round(rain, 1))
                temp_min = round(temp - 8 - random.uniform(0, 3), 2)
                temp_max = round(temp + 8 + random.uniform(0, 3), 2)
                temp_mean = round((temp_min + temp_max) / 2, 2)
                solar = round(random.uniform(10, 22) * solar_factor, 2)

                climate_rows.append(
                    {
                        "district_id": int(district["id"]),
                        "observation_date": f"{year}-{month:02d}-01",
                        "rainfall_mm": rainfall,
                        "temperature_min_c": temp_min,
                        "temperature_max_c": temp_max,
                        "temperature_mean_c": temp_mean,
                        "solar_radiation_mj_m2": solar,
                        "data_source": "NASA POWER",
                    }
                )

    climate_path = os.path.join(DATA_DIR, "chirps_2014_2024.csv")
    with open(climate_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "district_id",
                "observation_date",
                "rainfall_mm",
                "temperature_min_c",
                "temperature_max_c",
                "temperature_mean_c",
                "solar_radiation_mj_m2",
                "data_source",
            ],
        )
        writer.writeheader()
        writer.writerows(climate_rows)
    logger.info("Generated %d climate records → %s", len(climate_rows), climate_path)


def main():
    parser = argparse.ArgumentParser(description="Seed database for Nepal Ag Dashboard")
    parser.add_argument("--load-all", action="store_true", help="Load all seed data")
    parser.add_argument(
        "--generate-data", action="store_true", help="Generate synthetic CSV data"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Fail on validation errors"
    )
    parser.add_argument(
        "--init-schema", action="store_true", help="Initialize database schema"
    )
    args = parser.parse_args()

    if args.init_schema:
        logger.info("Initializing database schema...")
        init_db()
        status = check_db_connection()
        logger.info("Database status: %s", status)

    if args.generate_data:
        logger.info("Generating synthetic data...")
        generate_synthetic_data()

    if args.load_all or args.strict:
        logger.info("Loading all seed data (strict=%s)...", args.strict)
        results = asyncio.run(load_all(strict=args.strict))
        for table, count in results.items():
            logger.info("  %s: %d rows", table, count)

    logger.info("Done.")


if __name__ == "__main__":
    main()
