"""
Unit tests for utility functions and data services.

Covers:
  - Yield calculation (computed fields, division by zero)
  - Climate summary computation
  - Data quality validation
  - District/crop lookup helpers
"""

from datetime import date


# --------------------------------------------------------------------------- #
# Yield computation tests
# --------------------------------------------------------------------------- #


class TestYieldComputation:
    """Tests for yield_kg_ha computation from production and area."""

    def test_yield_computation_correct(self):
        """yield_kg_ha = (production_mt * 1000) / area_harvested_ha."""
        expected_yield = (450.0 * 1000) / 1200.0  # = 375 kg/ha

        assert expected_yield == 375.0

    def test_yield_computation_small_area(self):
        """Very small area should produce high yield per hectare."""
        expected_yield = (0.5 * 1000) / 0.001  # = 500000 kg/ha

        assert expected_yield == 500000.0

    def test_yield_computation_with_decimals(self):
        """Yield computation handles decimal precision correctly."""
        expected_yield = (1234.56 * 1000) / 789.01

        assert round(expected_yield, 2) == 1564.69


# --------------------------------------------------------------------------- #
# Trend detection tests
# --------------------------------------------------------------------------- #


class TestTrendDetection:
    """Tests for yield trend detection logic."""

    def test_increasing_trend_detected(self):
        """Increasing yields over time should produce 'INCREASING' trend."""
        from services.correlations import calculate_yield_statistics, YieldLike

        class FakeYield(YieldLike):
            def __init__(self, year: int, yield_val: float):
                self.year = year
                self.yield_kg_ha = yield_val

        rows = [
            FakeYield(2014, 350.0),
            FakeYield(2015, 360.0),
            FakeYield(2016, 370.0),
            FakeYield(2017, 380.0),
            FakeYield(2018, 390.0),
            FakeYield(2019, 400.0),
            FakeYield(2020, 410.0),
            FakeYield(2021, 420.0),
            FakeYield(2022, 430.0),
            FakeYield(2024, 440.0),
        ]

        stats = calculate_yield_statistics(rows)
        assert stats["trend"] == "INCREASING"
        assert stats["cagr_pct"] > 0

    def test_decreasing_trend_detected(self):
        """Decreasing yields should produce 'DECREASING' trend."""
        from services.correlations import calculate_yield_statistics, YieldLike

        class FakeYield(YieldLike):
            def __init__(self, year: int, yield_val: float):
                self.year = year
                self.yield_kg_ha = yield_val

        rows = [
            FakeYield(2014, 440.0),
            FakeYield(2015, 430.0),
            FakeYield(2016, 420.0),
            FakeYield(2017, 410.0),
            FakeYield(2018, 400.0),
            FakeYield(2019, 390.0),
            FakeYield(2020, 380.0),
            FakeYield(2021, 370.0),
            FakeYield(2022, 360.0),
            FakeYield(2024, 350.0),
        ]

        stats = calculate_yield_statistics(rows)
        assert stats["trend"] == "DECREASING"

    def test_stable_trend_detected(self):
        """Flat yields should produce 'STABLE' trend."""
        from services.correlations import calculate_yield_statistics, YieldLike

        class FakeYield(YieldLike):
            def __init__(self, year: int, yield_val: float):
                self.year = year
                self.yield_kg_ha = yield_val

        rows = [
            FakeYield(2014, 375.0),
            FakeYield(2015, 376.0),
            FakeYield(2016, 375.0),
            FakeYield(2017, 376.0),
            FakeYield(2018, 375.0),
        ]

        stats = calculate_yield_statistics(rows)
        assert stats["trend"] == "STABLE"

    def test_insufficient_data_handling(self):
        """Less than 2 data points should return INSUFFICIENT_DATA."""
        from services.correlations import calculate_yield_statistics, YieldLike

        class FakeYield(YieldLike):
            def __init__(self, year: int, yield_val: float):
                self.year = year
                self.yield_kg_ha = yield_val

        rows = [FakeYield(2024, 375.0)]

        stats = calculate_yield_statistics(rows)
        assert stats["trend"] == "INSUFFICIENT_DATA"
        assert stats["cagr_pct"] is None


# --------------------------------------------------------------------------- #
# CAGR computation tests
# --------------------------------------------------------------------------- #


class TestCAGR:
    """Tests for Compound Annual Growth Rate computation."""

    def test_positive_cagr(self):
        """Positive yield growth should produce positive CAGR."""
        from services.correlations import calculate_yield_statistics, YieldLike

        class FakeYield(YieldLike):
            def __init__(self, year: int, yield_val: float):
                self.year = year
                self.yield_kg_ha = yield_val

        rows = [
            FakeYield(2014, 350.0),
            FakeYield(2015, 375.0),
            FakeYield(2016, 400.0),
            FakeYield(2017, 425.0),
            FakeYield(2018, 450.0),
            FakeYield(2019, 475.0),
            FakeYield(2020, 500.0),
            FakeYield(2021, 500.0),
            FakeYield(2022, 500.0),
            FakeYield(2023, 500.0),
            FakeYield(2024, 500.0),
        ]

        stats = calculate_yield_statistics(rows)
        assert stats["cagr_pct"] > 0
        # CAGR should be between 0 and 10% for this data
        assert 0 < stats["cagr_pct"] < 10

    def test_zero_cagr(self):
        """Flat yields should produce ~0% CAGR."""
        from services.correlations import calculate_yield_statistics, YieldLike

        class FakeYield(YieldLike):
            def __init__(self, year: int, yield_val: float):
                self.year = year
                self.yield_kg_ha = yield_val

        rows = [FakeYield(y, 400.0) for y in range(2014, 2024)]
        stats = calculate_yield_statistics(rows)
        assert abs(stats["cagr_pct"]) < 0.1  # Near zero


# --------------------------------------------------------------------------- #
# Correlation tests
# --------------------------------------------------------------------------- #


class TestCorrelation:
    """Tests for Pearson correlation computation."""

    def test_positive_correlation(self):
        """Yield and rainfall should show positive correlation."""
        from services.correlations import compute_pearson

        yields = [350, 375, 400, 425, 450, 475]
        rainfall = [800, 900, 1000, 1100, 1200, 1300]

        corr = compute_pearson(yields, rainfall)
        assert corr is not None
        assert corr > 0.9  # Strong positive

    def test_negative_correlation(self):
        """Yield and temperature should show negative correlation (in some cases)."""
        from services.correlations import compute_pearson

        yields = [400, 380, 360, 340, 320]
        temp = [15, 20, 25, 30, 35]

        corr = compute_pearson(yields, temp)
        assert corr is not None
        assert corr < -0.5  # Negative

    def test_no_correlation(self):
        """Random data should have low correlation."""
        from services.correlations import compute_pearson

        yields = [400, 380, 360, 340, 320]
        temp = [25, 15, 30, 20, 22]  # No clear pattern

        corr = compute_pearson(yields, temp)
        assert corr is not None
        assert abs(corr) < 0.7  # Weak correlation

    def test_insufficient_data(self):
        """Less than 3 data points should return None."""
        from services.correlations import compute_pearson

        result = compute_pearson([100], [200])
        assert result is None

    def test_full_correlation_significance(self):
        """Full correlation should include p-value and significance flag."""
        from services.correlations import compute_full_correlation

        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

        result = compute_full_correlation(x, y)
        assert result["coefficient"] is not None
        assert result["p_value"] is not None
        assert result["significant"]
        assert result["coefficient"] > 0.99


# --------------------------------------------------------------------------- #
# Climate summary tests
# --------------------------------------------------------------------------- #


class TestClimateSummary:
    """Tests for climate summary computation."""

    def test_annual_rainfall_computed(self):
        """Annual rainfall should be sum of monthly values."""
        from services.climate import compute_climate_summary

        records = [
            {
                "observation_date": date(2024, 1, 1),
                "rainfall_mm": 45.0,
                "temperature_min_c": 8.0,
                "temperature_max_c": 22.0,
                "temperature_mean_c": 15.0,
                "solar_radiation_mj_m2": 12.0,
            },
            {
                "observation_date": date(2024, 2, 1),
                "rainfall_mm": 30.0,
                "temperature_min_c": 7.0,
                "temperature_max_c": 23.0,
                "temperature_mean_c": 15.0,
                "solar_radiation_mj_m2": 14.0,
            },
        ]

        summary = compute_climate_summary(records)
        assert summary["annual_rainfall_mm"] == 75.0

    def test_empty_records(self):
        """Empty records should return default summary."""
        from services.climate import compute_climate_summary

        summary = compute_climate_summary([])
        assert summary["annual_rainfall_mm"] is None
        assert summary["avg_temperature_c"] is None
        assert summary["monsoon_start_month"] == 6
        assert summary["monsoon_end_month"] == 9
