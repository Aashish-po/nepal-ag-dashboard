"""
Unit tests for business logic services.

Covers:
  - Forecasting (ARIMA, exponential smoothing, model selection)
  - Data quality validation
  - ETL helpers
"""


# --------------------------------------------------------------------------- #
# Forecasting tests
# --------------------------------------------------------------------------- #


class TestForecasting:
    """Tests for forecast model functions."""

    def test_arima_returns_forecasts(self):
        """ARIMA forecasting should return forecast list and diagnostics."""
        from services.forecasting import forecast_arima

        yields = [375.0, 384.0, 395.0, 388.0, 392.0, 378.0, 385.0, 390.0, 387.0, 391.0]
        years = list(range(2014, 2024))

        result = forecast_arima(yields, years, periods=12)

        assert result["model"] == "ARIMA"
        assert len(result["forecasts"]) == 12
        assert len(result["lower_ci"]) == 12
        assert len(result["upper_ci"]) == 12
        assert result["rmse"] >= 0
        assert result["mae"] >= 0

    def test_exp_smoothing_returns_forecasts(self):
        """Exponential smoothing should return forecast list and diagnostics."""
        from services.forecasting import forecast_exp_smoothing

        yields = [375.0, 384.0, 395.0, 388.0, 392.0, 378.0, 385.0, 390.0, 387.0, 391.0]
        years = list(range(2014, 2024))

        result = forecast_exp_smoothing(yields, years, periods=12)

        assert result["model"] == "ExponentialSmoothing"
        assert len(result["forecasts"]) == 12

    def test_model_selection(self):
        """Model selector should return a valid model name."""
        from services.forecasting import select_best_model

        yields = [350.0, 360.0, 370.0, 380.0, 390.0, 400.0, 410.0, 420.0, 430.0, 440.0]

        model = select_best_model(yields, 12)
        assert model in ("ARIMA", "ExponentialSmoothing")

    def test_train_forecast_short_data(self):
        """Forecasting with limited data (<5 years) should use moving average."""
        from services.forecasting import train_forecast

        yields = [375.0, 384.0, 395.0]  # Only 3 years
        years = [2022, 2023, 2024]

        result = train_forecast(yields, years, months_ahead=12)

        assert result["model"] == "MovingAverage"
        assert len(result["forecasts"]) == 12

    def test_forecast_confidence_intervals(self):
        """Lower CI should be below forecast, upper CI above."""
        from services.forecasting import train_forecast

        yields = [350.0, 360.0, 370.0, 380.0, 390.0, 400.0, 410.0, 420.0, 430.0, 440.0]
        years = list(range(2014, 2024))

        result = train_forecast(yields, years, months_ahead=36)

        for f, lo, hi in zip(
            result["forecasts"], result["lower_ci"], result["upper_ci"]
        ):
            assert lo <= f <= hi

    def test_forecast_rmse_reasonable(self):
        """RMSE should be a reasonable fraction of the yield values."""
        from services.forecasting import train_forecast

        yields = [350.0, 360.0, 370.0, 380.0, 390.0, 400.0, 410.0, 420.0, 430.0, 440.0]
        years = list(range(2014, 2024))

        result = train_forecast(yields, years, months_ahead=12)

        # RMSE should be less than 50% of mean yield
        mean_yield = sum(yields) / len(yields)
        assert result["rmse"] < mean_yield * 0.5  # Generous bound


# --------------------------------------------------------------------------- #
# Data validation tests
# --------------------------------------------------------------------------- #


class TestDataValidation:
    """Tests for ETL data validation functions."""

    def test_yields_validation_negative_production(self):
        """Negative production should be flagged as error."""
        from services.etl import validate_yields
        import pandas as pd

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
        from services.etl import validate_yields
        import pandas as pd

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
        from services.etl import validate_yields
        import pandas as pd

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
        from services.etl import validate_yields
        import pandas as pd

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
        from services.etl import validate_climate
        import pandas as pd

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
        from services.etl import validate_climate
        import pandas as pd

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


# --------------------------------------------------------------------------- #
# Cache service tests
# --------------------------------------------------------------------------- #


class TestCacheService:
    """Tests for the Redis cache service (mocking not required for basic import)."""

    def test_cache_functions_exist(self):
        """Cache service should expose get_cached, set_cached, invalidate_cache."""
        import services.cache as cache

        assert hasattr(cache, "get_cached")
        assert hasattr(cache, "set_cached")
        assert hasattr(cache, "invalidate_cache")
        assert hasattr(cache, "invalidate_all_cache")

    def test_cache_returns_none_when_no_redis(self):
        """When Redis is not configured, get_cached should return None."""
        from services.cache import get_cached

        # Without REDIS_URL set, should return None
        result = get_cached.__wrapped__ if hasattr(get_cached, "__wrapped__") else None
        # The function is async; test it returns None when Redis unavailable
        import asyncio

        result = asyncio.run(get_cached("test:key"))
        assert result is None
