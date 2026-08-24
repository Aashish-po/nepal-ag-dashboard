from api.routes.export_crops import _export_crop_info


def test_revenue_computed_from_production_and_price():
    info = _export_crop_info(
        crop_id=5,
        crop_name="Cardamom",
        production_mt=5000.0,
        area_harvested_ha=8500.0,
        yield_kg_ha=588.0,
        avg_price_usd_per_mt=8000.0,
        main_export_countries=["India", "Japan"],
        season_start_month=9,
        season_end_month=12,
    )
    assert info.estimated_revenue_usd == 40_000_000.0
    assert info.export_potential_mt == 5000.0
    assert info.export_season is not None
    assert info.export_season.start_month == 9
    assert info.main_export_countries == ["India", "Japan"]


def test_missing_price_or_season_degrades_gracefully():
    info = _export_crop_info(
        crop_id=6,
        crop_name="Ginger",
        production_mt=5000.0,
        area_harvested_ha=None,
        yield_kg_ha=None,
        avg_price_usd_per_mt=None,
        main_export_countries=None,
        season_start_month=None,
        season_end_month=None,
    )
    assert info.estimated_revenue_usd is None
    assert info.export_season is None
    assert info.main_export_countries == []
