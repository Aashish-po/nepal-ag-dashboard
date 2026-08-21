"""
Test fixture data loader — provides sample data for integration tests
when a real database may not be available.
"""

import json
import os

_fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")


def _load_json(filename: str):
    fpath = os.path.join(_fixtures_dir, filename)
    if os.path.exists(fpath):
        with open(fpath, encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_districts():
    """Return sample districts for testing."""
    data = _load_json("districts.json")
    return data.get(
        "districts",
        [
            {
                "id": 1,
                "name": "Kathmandu",
                "province": "Bagmati",
                "region": "Hill",
                "latitude": 27.7172,
                "longitude": 85.3240,
                "population": 1200000,
                "area_sq_km": 899.25,
            },
        ],
    )


def get_crops():
    """Return sample crops for testing."""
    return [
        {
            "id": 1,
            "name": "Rice",
            "fao_code": "F0027",
            "category": "Cereal",
            "unit": "MT",
            "is_export_crop": False,
            "is_subsistence": True,
        },
        {
            "id": 5,
            "name": "Cardamom",
            "fao_code": "F0717",
            "category": "Spice",
            "unit": "MT",
            "is_export_crop": True,
            "is_subsistence": False,
        },
    ]


def get_yields():
    """Return sample yields for testing."""
    data = _load_json("yields.json")
    return data.get("yields", [])


def get_climate():
    """Return sample climate data for testing."""
    data = _load_json("climate.json")
    return data.get("climate", [])
