"""Regenerate Nepal districts GeoJSON from source data."""

import json
from pathlib import Path
from typing import Any


def load_districts_json(filepath: Path) -> dict[str, Any]:
    """Load districts data from JSON file."""
    with filepath.open("r", encoding="utf-8") as f:
        return json.load(f)


def create_geojson_feature(district: dict[str, Any]) -> dict[str, Any]:
    """Create a GeoJSON feature from district data."""
    properties = {
        "id": district["properties"]["id"],
        "district_name": district["properties"]["district_name"],
        "province": district["properties"]["province"],
        "region": district["properties"]["region"],
        "census_2021_population": district["properties"]["census_2021_population"],
        "area_sq_km": district["properties"]["area_sq_km"],
        "population_density": district["properties"]["population_density"],
        "urban": district["properties"]["urban"],
        "headquarters": district["properties"]["headquarters"],
    }

    # Use existing geometry (Point) - in production, replace with Polygon from shapefile
    geometry = district["geometry"]

    return {
        "type": "Feature",
        "properties": properties,
        "geometry": geometry,
    }


def main() -> None:
    """Main function to regenerate GeoJSON."""
    base_path = Path(__file__).parent.parent
    input_path = base_path / "frontend" / "src" / "data" / "nepal_districts.json"
    output_path = base_path / "data" / "nepal_districts.geojson"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load source data
    source_data = load_districts_json(input_path)

    # Create new features (deduplicate by district_name)
    seen_names: set[str] = set()
    features: list[dict[str, Any]] = []

    for district in source_data.get("features", []):
        name = district["properties"]["district_name"]
        if name in seen_names:
            raise ValueError(f"Duplicate district_name in source data: {name}")
        seen_names.add(name)
        features.append(create_geojson_feature(district))

    if len(features) != 77:
        raise ValueError(f"Expected 77 districts, got {len(features)}")

    # Create FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    # Write output
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"Generated {output_path} with {len(features)} districts")


if __name__ == "__main__":
    main()
