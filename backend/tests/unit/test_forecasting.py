"""
Unit tests for backend/services/forecasting.py.

Covers:
  - _build_monthly_from_annual (annual→monthly upsampling)
  - train_district_crop_forecast success and insufficient-data paths
  - _select_model picks lower-AIC candidate and returns None when all fail
"""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

# Ensure backend/ is on sys.path so ``services.forecasting`` resolves.
sys.path.insert(0, "backend")
from services.forecasting import (
    _build_monthly_from_annual,
    _select_model,
    train_district_crop_forecast,
)

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _yield_record(year: int, yield_kg_ha: float) -> SimpleNamespace:
    return SimpleNamespace(year=year, yield_kg_ha=yield_kg_ha)


def _mock_db(yield_rows: list[SimpleNamespace]) -> MagicMock:
    """Return a mock session that hands back yield_rows for yield queries."""

    db = MagicMock()

    def execute_side_effect(stmt):
        stmt_str = str(stmt).lower()
        if "yield_kg_ha" in stmt_str and "district_id" in stmt_str:
            result = MagicMock()
            result.all.return_value = yield_rows
            return result
        if (
            "district_id" in stmt_str
            and "crop_id" in stmt_str
            and "distinct" in stmt_str
        ):
            result = MagicMock()
            result.all.return_value = [(1, 1)]
            return result
        result = MagicMock()
        result.all.return_value = []
        return result

    db.execute.side_effect = execute_side_effect
    return db


# --------------------------------------------------------------------------- #
# _build_monthly_from_annual
# --------------------------------------------------------------------------- #


class TestBuildMonthlyFromAnnual:
    """Tests for annual → monthly upsampling."""

    def test_repeats_each_year_12_times(self):
        """Each year's value should appear 12 times in the resulting series."""
        years = [2020, 2021]
        values = np.array([100.0, 200.0])
        series = _build_monthly_from_annual(years, values)

        assert len(series) == 24
        assert all(v == 100.0 for v in series.iloc[:12])
        assert all(v == 200.0 for v in series.iloc[12:])

    def test_index_starts_at_january(self):
        """First element should be January 1st of the first year."""
        years = [2020]
        values = np.array([50.0])
        series = _build_monthly_from_annual(years, values)

        assert len(series) == 12
        assert series.index[0].year == 2020
        assert series.index[0].month == 1
        assert series.index[0].day == 1
        assert series.index[11].month == 12


# --------------------------------------------------------------------------- #
# train_district_crop_forecast
# --------------------------------------------------------------------------- #


class TestTrainDistrictCropForecast:
    """Tests for the main training entry point."""

    def test_returns_zero_when_insufficient_data(self):
        """Fewer than 5 years of data should skip training."""
        db = _mock_db([_yield_record(2022, 100.0)])

        n = train_district_crop_forecast(db, district_id=1, crop_id=1, months_ahead=12)
        assert n == 0

    def test_writes_forecast_rows_on_success(self):
        """Valid input should write months_ahead rows to the forecasts table."""
        db = _mock_db([_yield_record(y, 100.0 + y) for y in range(2018, 2025)])

        with patch("services.forecasting._upsert_forecasts") as mock_upsert:
            n = train_district_crop_forecast(
                db, district_id=1, crop_id=1, months_ahead=12
            )
            assert n == 12
            mock_upsert.assert_called_once()
            records = mock_upsert.call_args[0][1]
            assert len(records) == 12
            for rec in records:
                assert "forecast_yield_kg_ha" in rec
                assert "lower_ci_95" in rec
                assert "upper_ci_95" in rec
                assert "forecast_model" in rec
                assert rec["district_id"] == 1
                assert rec["crop_id"] == 1


# --------------------------------------------------------------------------- #
# _select_model
# --------------------------------------------------------------------------- #


class TestSelectModel:
    """Tests for SARIMA vs ExponentialSmoothing model selection by AIC."""

    def test_returns_best_aic_model(self):
        """_select_model should pick the model with the lower AIC."""
        series = pd.Series(np.ones(36) * 100.0)
        result = _select_model(series)

        assert result is not None
        assert result.model_name in ("SARIMAX", "ExponentialSmoothing")
        assert len(result.forecast) == 36
        assert len(result.ci_width) == 36
        assert result.rmse >= 0
        assert result.mae >= 0
        assert result.mape >= 0

    def test_returns_none_when_all_models_fail(self):
        """If every model raises, _select_model should return None."""
        series = pd.Series([1.0] * 12)

        class _ForecastError(Exception):
            pass

        def _boom(_series):
            raise _ForecastError("boom")

        # Patch _select_model's globals so its local lookups of _fit_sarimax
        # and _fit_es resolve to the failing stubs at call time.
        with patch.dict(
            _select_model.__globals__,
            {"_fit_sarimax": _boom, "_fit_es": _boom},
        ):
            result = _select_model(series)
            assert result is None
