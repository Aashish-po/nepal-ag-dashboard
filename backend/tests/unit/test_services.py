"""
Unit tests for business logic services.

Covers:
  - Data quality validation
  - ETL helpers
"""

# --------------------------------------------------------------------------- #
# Data validation tests
# --------------------------------------------------------------------------- #


class TestDataValidation:
    """Tests for ETL data validation functions."""

    def test_yields_validation_negative_production(self):
        """Negative production should be flagged as error."""
        import pandas as pd
        from services.etl import validate_yields

        df = pd.DataFrame(
            {
                "district_id": [1, 1],
                "crop_id": [1, 1],
                "year": [2024, 2024],
                "production_mt": [-100, 450000],
                "area_harvested_ha": [1000, 1200000],
                "yield_kg_ha": [None, 375],
                "data_source": ["FAOSTAT", "FAOSTAT"],
                "data_quality": ["Official", "Official"],
            }
        )

        report = validate_yields(df)
        assert len(report["errors"]) > 0
        assert any("negative production" in e.lower() for e in report["errors"])

    def test_yields_validation_zero_area(self):
        """Zero area should be flagged as error."""
        import pandas as pd
        from services.etl import validate_yields

        df = pd.DataFrame(
            {
                "district_id": [1],
                "crop_id": [1],
                "year": [2024],
                "production_mt": [450000],
                "area_harvested_ha": [0],
                "yield_kg_ha": [None],
                "data_source": ["FAOSTAT"],
                "data_quality": ["Official"],
            }
        )

        report = validate_yields(df)
        assert len(report["errors"]) > 0
        assert any("zero or negative" in e.lower() for e in report["errors"])

    def test_yields_validation_valid_data(self):
        """Valid yield data should produce no errors."""
        import pandas as pd
        from services.etl import validate_yields

        df = pd.DataFrame(
            {
                "district_id": [1],
                "crop_id": [1],
                "year": [2024],
                "production_mt": [450000],
                "area_harvested_ha": [1200000],
                "yield_kg_ha": [375],
                "data_source": ["FAOSTAT"],
                "data_quality": ["Official"],
            }
        )

        report = validate_yields(df)
        assert len(report["errors"]) == 0

    def test_yields_validation_year_range(self):
        """Years outside 2014-2024 should be flagged."""
        import pandas as pd
        from services.etl import validate_yields

        df = pd.DataFrame(
            {
                "district_id": [1],
                "crop_id": [1],
                "year": [2010],
                "production_mt": [450000],
                "area_harvested_ha": [1200000],
                "yield_kg_ha": [375],
                "data_source": ["FAOSTAT"],
                "data_quality": ["Official"],
            }
        )

        report = validate_yields(df)
        assert any("year outside" in e.lower() for e in report["errors"])

    def test_climate_validation_negative_rainfall(self):
        """Negative rainfall should be flagged."""
        import pandas as pd
        from services.etl import validate_climate

        df = pd.DataFrame(
            {
                "district_id": [1],
                "observation_date": ["2024-01-01"],
                "rainfall_mm": [-10.0],
                "temperature_min_c": [8.0],
                "temperature_max_c": [22.0],
                "temperature_mean_c": [15.0],
                "solar_radiation_mj_m2": [12.0],
                "data_source": ["NASA POWER"],
            }
        )

        report = validate_climate(df)
        assert any("negative rainfall" in e.lower() for e in report["errors"])

    def test_climate_validation_temp_order(self):
        """Min temp >= max temp should be flagged."""
        import pandas as pd
        from services.etl import validate_climate

        df = pd.DataFrame(
            {
                "district_id": [1],
                "observation_date": ["2024-01-01"],
                "rainfall_mm": [45.0],
                "temperature_min_c": [25.0],  # Higher than max
                "temperature_max_c": [22.0],
                "temperature_mean_c": [23.5],
                "solar_radiation_mj_m2": [12.0],
                "data_source": ["NASA POWER"],
            }
        )

        report = validate_climate(df)
        assert any("min" in e.lower() for e in report["errors"])


class TestUpsertDateCoercion:
    """Guard: date-typed columns must reach the DB as real date objects.

    Regression test — CSVs supply dates as strings. Postgres coerces them, but
    SQLite's Date bind processor rejects strings, so _upsert_table_rows must
    convert them. This would fail before that coercion existed.
    """

    def test_climate_string_date_stored_as_date(self, tmp_path, monkeypatch):
        import datetime

        import pandas as pd
        from api.models.db_models import Base
        from services.etl import load_climate_from_chirps
        from sqlalchemy import create_engine, select

        db_url = f"sqlite:///{tmp_path / 'etl.db'}"
        monkeypatch.setenv("DATABASE_URL", db_url)

        engine = create_engine(db_url)
        climate = Base.metadata.tables["climate"]
        climate.create(engine)  # single table -> skips the ARRAY table SQLite rejects

        df = pd.DataFrame(
            {
                "district_id": [1],
                "observation_date": ["2024-01-01"],  # string, as read from CSV
                "rainfall_mm": [45.0],
                "temperature_min_c": [10.0],
                "temperature_max_c": [22.0],
                "temperature_mean_c": [16.0],
                "solar_radiation_mj_m2": [12.0],
                "data_source": ["NASA POWER"],
            }
        )

        assert load_climate_from_chirps(data=df) == 1

        with engine.connect() as conn:
            stored = conn.execute(select(climate.c.observation_date)).scalar_one()
        assert stored == datetime.date(2024, 1, 1)
