"""Build the merged Nepal districts GeoJSON.

Combines:
- The high-resolution Polygon source (Nepal_Administrative_Boundary_District.geojson)
- Canonical district metadata (backend/data/districts.csv)

Writes:
- frontend/src/data/nepal_districts.json  (Map page import)
- data/nepal_districts.geojson            (committed export, regenerated from source)

Polygons are simplified with shapely (Douglas-Peucker, preserve_topology) so
the Map page can bundle them as a single JSON module without a 50MB initial
payload. Tolerance is empirically chosen for an ~800x500 viewport: vertex
density above ~150/district is invisible at this scale, so simplification
drops 90-95% of vertices with no visible quality loss.

Spelling: the high-res source's district names are authoritative and propagate
into the canonical CSV. Province names in the source use the official
"Province No N" / "X Pradesh" forms; we normalize to the canonical English
names already used in the rest of the app.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

REPO = Path(__file__).resolve().parent.parent
SOURCE_POLYGONS = REPO / "Nepal_Administrative_Boundary_District.geojson"
DISTRICTS_CSV = REPO / "backend" / "data" / "districts.csv"
OUT_MAP_JSON = REPO / "frontend" / "src" / "data" / "nepal_districts.json"
OUT_EXPORT_GEOJSON = REPO / "data" / "nepal_districts.geojson"

# High-res source spelling -> canonical name (as already used in districts.csv)
NAME_ALIASES: dict[str, str] = {
    "Chitawan": "Chitwan",
    "Kabhrepalanchok": "Kavrepalanchok",
    "Kapilbastu": "Kapilvastu",
    "Makawanpur": "Makwanpur",
    "Tanahu": "Tanahun",
}

# High-res source PR_NAME -> canonical province (matches districts.csv)
PROVINCE_ALIASES: dict[str, str] = {
    "Province No 1": "Koshi",
    "Province No 2": "Madhesh",
    "Bagmati Pradesh": "Bagmati",
    "Gandaki Pradesh": "Gandaki",
    "Province No 5": "Lumbini",
    "Karnali Pradesh": "Karnali",
    "Sudurpashchim Pradesh": "Sudurpashchim",
}

# 0.0005 deg ~ 50m at Nepal's latitude; below d3-geo's snap threshold for an
# 800x500 viewport. Tighter if you zoom in.
SIMPLIFY_TOLERANCE = 0.0005


def canonical_name(source_name: str) -> str:
    return NAME_ALIASES.get(source_name, source_name)


def canonical_province(source_pr: str) -> str:
    if source_pr in PROVINCE_ALIASES:
        return PROVINCE_ALIASES[source_pr]
    if source_pr.endswith(" Pradesh"):
        return source_pr[: -len(" Pradesh")]
    raise ValueError(f"Unknown source PR_NAME: {source_pr!r}")


def load_polygons() -> dict[str, dict]:
    with SOURCE_POLYGONS.open("r", encoding="utf-8") as f:
        gj = json.load(f)
    out: dict[str, dict] = {}
    for feat in gj["features"]:
        src_name = feat["properties"]["DISTRICT"]
        canon = canonical_name(src_name)
        if canon in out:
            raise ValueError(f"Duplicate canonical name in source: {canon}")
        out[canon] = {
            "geometry": shape(feat["geometry"]),
            "object_id": feat["properties"]["OBJECTID"],
            "province": canonical_province(feat["properties"]["PR_NAME"]),
        }
    return out


def load_canonical() -> pd.DataFrame:
    df = pd.read_csv(DISTRICTS_CSV)
    expected = {
        "id",
        "name",
        "province",
        "region",
        "latitude",
        "longitude",
        "population",
        "area_sq_km",
    }
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"districts.csv missing columns: {missing}")
    return df


def build_feature(row: pd.Series, geom) -> dict:
    area = float(row["area_sq_km"])
    pop = int(row["population"])
    props = {
        "id": int(row["id"]),
        "district_name": str(row["name"]),
        "province": str(row["province"]),
        "region": str(row["region"]),
        "census_2021_population": pop,
        "area_sq_km": area,
        "population_density": round(pop / area, 1) if area > 0 else 0.0,
        "urban": False,
        "headquarters": str(row["name"]),
    }
    return {
        "type": "Feature",
        "properties": props,
        "geometry": mapping(geom),
    }


def main() -> None:
    polygons = load_polygons()
    df = load_canonical()

    if len(df) != 77:
        raise ValueError(f"Expected 77 districts in CSV, got {len(df)}")
    if len(polygons) != 77:
        raise ValueError(f"Expected 77 polygons in source, got {len(polygons)}")

    missing = sorted({canonical_name(str(n)) for n in df["name"]} - set(polygons))
    if missing:
        raise ValueError(f"CSV districts with no polygon: {missing}")
    extra = sorted(set(polygons) - {canonical_name(str(n)) for n in df["name"]})
    if extra:
        raise ValueError(f"Polygons with no CSV row: {extra}")

    # Sanity: CSV is canonical; source must agree on province
    mismatched = [
        (
            canonical_name(str(n)),
            row["province"],
            polygons[canonical_name(str(n))]["province"],
        )
        for n, row in df.set_index("name").iterrows()
        if polygons[canonical_name(str(n))]["province"] != row["province"]
    ]
    if mismatched:
        raise ValueError(f"Province mismatch between polygon and CSV: {mismatched}")

    # Simplify each district polygon
    features: list[dict] = []
    for _, row in df.iterrows():
        name = canonical_name(str(row["name"]))
        simple_geom = polygons[name]["geometry"].simplify(
            SIMPLIFY_TOLERANCE, preserve_topology=True
        )
        features.append(build_feature(row, simple_geom))

    # Country outline: dissolve all districts into one polygon
    unioned = unary_union(
        [polygons[canonical_name(str(n))]["geometry"] for n in df["name"]]
    )
    outline = unioned.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
    outline_feature = {
        "type": "Feature",
        "properties": {
            "id": 0,
            "district_name": "Nepal",
            "province": "",
            "region": "",
            "census_2021_population": 0,
            "area_sq_km": 0.0,
            "population_density": 0.0,
            "urban": False,
            "headquarters": "Nepal",
        },
        "geometry": mapping(outline),
    }

    collection = {
        "type": "FeatureCollection",
        "features": [outline_feature, *features],
    }

    OUT_MAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_MAP_JSON.open("w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, separators=(",", ":"))

    OUT_EXPORT_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_EXPORT_GEOJSON.open("w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)

    map_kb = OUT_MAP_JSON.stat().st_size / 1024
    export_kb = OUT_EXPORT_GEOJSON.stat().st_size / 1024
    print(f"Wrote {OUT_MAP_JSON.relative_to(REPO)} ({map_kb:,.1f} KB)")
    print(f"Wrote {OUT_EXPORT_GEOJSON.relative_to(REPO)} ({export_kb:,.1f} KB)")
    print(
        f"{len(features)} districts + 1 country outline, "
        f"simplified to tolerance={SIMPLIFY_TOLERANCE} deg"
    )


if __name__ == "__main__":
    main()
