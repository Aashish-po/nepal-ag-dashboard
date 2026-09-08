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
from shapely import orient_polygons
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

# Nepal WGS84 bounds (conservative — 1° buffer so clipped border districts still pass).
NEPAL_BOUNDS = (79.0, 25.0, 89.0, 31.5)  # min_lng, min_lat, max_lng, max_lat


def _validate_feature(feat: dict) -> None:
    """Validate a single feature's geometry + population (fails fast)."""
    props = feat.get("properties", {})
    name = props.get("district_name") or props.get("name") or "unknown"
    is_outline = props.get("id") == 0
    geom = shape(feat["geometry"])
    if geom.is_empty:
        raise ValueError(f"Empty geometry for {name!r}")
    if not geom.is_valid:
        raise ValueError(f"Invalid geometry for {name!r}: {geom.wkt[:200]}")
    min_lng, min_lat, max_lng, max_lat = NEPAL_BOUNDS
    minx, miny, maxx, maxy = geom.bounds
    if minx < min_lng or maxx > max_lng or miny < min_lat or maxy > max_lat:
        raise ValueError(
            f"Geometry for {name!r} bounds {geom.bounds} outside Nepal {NEPAL_BOUNDS} — "
            "likely lat/lng swap or screen-space coords"
        )
    if feat["geometry"]["type"] not in ("Polygon", "MultiPolygon", "Point"):
        raise ValueError(
            f"Unexpected geometry type for {name!r}: {feat['geometry']['type']}"
        )
    # population 0 is implausible for Nepal (every district >5k); flag so
    # Map.tsx doesn't have to render '—' silently for bad upstream data.
    if not is_outline:
        pop = props.get("census_2021_population", props.get("population"))
        if pop is not None and (not isinstance(pop, (int, float)) or pop <= 0):
            raise ValueError(f"Invalid population for {name!r}: {pop!r}")


def _validate_features(features: list[dict], outline: dict | None = None) -> None:
    """Fail fast if any geometry would corrupt the Map page.

    Previously skipped: coordinate range + polygon validity. Called before
    any file is written so a bad upstream source never lands in
    frontend/src/data/nepal_districts.json.
    """
    for feat in features:
        _validate_feature(feat)
    if outline is not None:
        _validate_feature(outline)
    if len(features) != 77:
        raise ValueError(f"Expected 77 district features, got {len(features)}")


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
            "geometry": orient_polygons(shape(feat["geometry"]), exterior_cw=True),
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
        # ponytail: source rings are CCW; d3-geo expects exterior CW for small
        # spherical area — without this every polygon is ~99% of the earth.
        simple_geom = orient_polygons(simple_geom, exterior_cw=True)
        features.append(build_feature(row, simple_geom))

    # Country outline: dissolve all districts into one polygon
    unioned = unary_union(
        [polygons[canonical_name(str(n))]["geometry"] for n in df["name"]]
    )
    outline = unioned.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
    outline = orient_polygons(outline, exterior_cw=True)
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

    # District centroids as Point features (same props as the polygon, Point geom)
    # ponytail: representative_point() vs centroid() — representative_point
    # guarantees the marker is inside the polygon, useful for non-convex districts.
    centroid_features: list[dict] = []
    for poly_feat in features:
        centroid_features.append(
            {
                "type": "Feature",
                "properties": dict(poly_feat["properties"]),
                "geometry": mapping(
                    shape(poly_feat["geometry"]).representative_point()
                ),
            }
        )

    # Previously skipped: fail fast before writing so a bad upstream source
    # never lands in frontend/src/data/nepal_districts.json.
    _validate_features(features, outline_feature)
    for cf in centroid_features:
        _validate_feature(cf)

    collection = {
        "type": "FeatureCollection",
        "features": [outline_feature, *features, *centroid_features],
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
        f"{len(features)} districts + 1 country outline + {len(centroid_features)} "
        f"centroid points, simplified to tolerance={SIMPLIFY_TOLERANCE} deg"
    )


if __name__ == "__main__":
    main()
