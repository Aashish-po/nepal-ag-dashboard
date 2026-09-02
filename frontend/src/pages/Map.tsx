import { useMemo, useState } from "react";
import { MapPin, X } from "lucide-react";
import { Button } from "@/shadcn/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";
import nepalGeoJSON from "@/data/nepal_districts.json";
import type { FeatureCollection } from "geojson";
import * as d3Geo from "d3-geo";

const PROVINCE_COLORS: Record<string, string> = {
  Koshi: "#2E7D32",
  Madhesh: "#1976D2",
  Bagmati: "#FB8C00",
  Gandaki: "#C62828",
  Lumbini: "#6A1B9A",
  Karnali: "#00796B",
  Sudurpashchim: "#E65100",
};

const DEFAULT_COLOR = "#90A4AE";

export interface DistrictInfo {
  /** Stable numeric id from GeoJSON properties; 0 means missing/fallback. */
  id: number;
  /** Derivable fallback key used when id is missing or 0. */
  uid: string;
  name: string;
  province: string;
  region: string;
  population: number;
  area_sq_km: number;
}

interface DistrictPath {
  d: string;
  district: DistrictInfo;
  color: string;
}

interface DistrictCircle {
  cx: number;
  cy: number;
  district: DistrictInfo;
  color: string;
}

export function Map() {
  const [selected, setSelected] = useState<DistrictInfo | null>(null);

  const { viewBox, paths, circles } = useMemo(() => {
    const collection = nepalGeoJSON as FeatureCollection;
    const proj = d3Geo.geoMercator();

    // fitSize mutates in-place: sets scale + translate so the collection fills [800,500]
    proj.fitSize([800, 500], collection);

    // Pass projection at construction time so types resolve cleanly
    const geoPath = d3Geo.geoPath(proj);
    const bounds = geoPath.bounds(collection);
    const pad = 8;
    const vb = {
      x: bounds[0][0] - pad,
      y: bounds[0][1] - pad,
      w: bounds[1][0] - bounds[0][0] + pad * 2,
      h: bounds[1][1] - bounds[0][1] + pad * 2,
    };

    const districtPaths: DistrictPath[] = [];
    const districtCircles: DistrictCircle[] = [];
    for (const feature of collection.features) {
      const props = (feature.properties ?? {}) as Record<string, unknown>;
      if (props.district_name == null && props.name == null) continue;
      const rawId = Number(props.id ?? 0);
      const name = String(props.district_name ?? props.name ?? "Unknown");
      const province = String(props.province ?? "Unknown");
      const district: DistrictInfo = {
        id: rawId || 0,
        uid: rawId ? String(rawId) : `${name}__${province}`,
        name,
        province,
        region: String(props.region ?? "Unknown"),
        population: Number(props.census_2021_population ?? props.population ?? 0),
        area_sq_km: Number(props.area_sq_km ?? 0),
      };
      if (!feature.geometry) continue;
      const color = PROVINCE_COLORS[district.province] ?? DEFAULT_COLOR;

      // Polygon/MultiPolygon geometries render as paths; geoPath returns undefined for Point geometries.
      const geomType = feature.geometry.type;
      if (geomType === "Polygon" || geomType === "MultiPolygon") {
        const d = geoPath(feature);
        if (d) districtPaths.push({ d, district, color });
        continue;
      }

      // Centroid markers: dataset stores Points for each district. Project coordinates manually.
      if (geomType === "Point") {
        const point = proj(feature.geometry.coordinates as [number, number]);
        if (point) {
          const [cx, cy] = point;
          districtCircles.push({ cx, cy, district, color });
        }
      }
    }

    return { viewBox: `${vb.x} ${vb.y} ${vb.w} ${vb.h}`, paths: districtPaths, circles: districtCircles };
  }, []);

  const setFill = (el: SVGGraphicsElement | null, color: string) => {
    el?.setAttribute("fill", color);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-h1 font-bold mb-6">District Map</h1>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Nepal Districts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="w-full overflow-x-auto">
              <svg
                viewBox={viewBox}
                className="w-full max-w-200 h-auto"
                style={{ display: "block" }}
              >
                {paths.map(({ d, district, color }) => {
                  const isActive = selected?.uid === district.uid;
                  return (
                    <g
                      key={`path-${district.uid}`}
                      style={{ cursor: "pointer" }}
                      onMouseEnter={(e) => {
                        const p = (e.currentTarget as SVGGElement).querySelector("path");
                        setFill(p as SVGPathElement | null, "#81C784");
                      }}
                      onMouseLeave={(e) => {
                        const p = (e.currentTarget as SVGGElement).querySelector("path");
                        setFill(p as SVGPathElement | null, isActive ? color : "transparent");
                      }}
                      onClick={() =>
                        setSelected((prev) => (prev?.uid === district.uid ? null : district))
                      }
                      tabIndex={0}
                      role="button"
                      aria-label={`${district.name} district`}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          setSelected((prev) => (prev?.uid === district.uid ? null : district));
                        }
                      }}
                    >
                      <title>{district.name}</title>
                      <path
                        d={d}
                        fill={isActive ? color : "transparent"}
                        stroke={color}
                        strokeWidth={isActive ? 2 : 0.5}
                        style={{ transition: "fill 0.15s" }}
                      />
                    </g>
                  );
                })}
                {circles.map(({ cx, cy, district, color }) => {
                  const isActive = selected?.uid === district.uid;
                  return (
                    <g
                      key={`circle-${district.uid}`}
                      style={{ cursor: "pointer" }}
                      onClick={() =>
                        setSelected((prev) => (prev?.uid === district.uid ? null : district))
                      }
                      tabIndex={0}
                      role="button"
                      aria-label={`${district.name} district`}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          setSelected((prev) => (prev?.uid === district.uid ? null : district));
                        }
                      }}
                    >
                      <title>{district.name}</title>
                      <circle
                        cx={cx}
                        cy={cy}
                        r={isActive ? 6 : 4}
                        fill={isActive ? color : "transparent"}
                        stroke={color}
                        strokeWidth={isActive ? 2 : 1}
                        style={{ transition: "r 0.15s, fill 0.15s, stroke-width 0.15s" }}
                      />
                    </g>
                  );
                })}
              </svg>
            </div>
            <p className="text-sm text-text-muted mt-3">
              Click a district to view details. Colors indicate province.
            </p>
            <div className="flex flex-wrap gap-3 mt-3">
              {Object.entries(PROVINCE_COLORS).map(([prov, c]) => (
                <span key={prov} className="flex items-center gap-1 text-xs text-text-secondary">
                  <span
                    className="w-3 h-3 rounded-sm inline-block shrink-0"
                    style={{ background: c }}
                  />
                  {prov}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>

        {selected ? (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle>{selected.name}</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setSelected(null)}>
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-text-secondary">
                  <MapPin className="w-4 h-4 shrink-0" />
                  <span>
                    {selected.province} · {selected.region}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Population</p>
                  <p className="text-xl font-bold">{selected.population.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Area</p>
                  <p className="text-xl font-bold">
                    {selected.area_sq_km.toLocaleString()} km²
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Province</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className="inline-block w-4 h-4 rounded-sm shrink-0"
                      style={{
                        background: PROVINCE_COLORS[selected.province] ?? DEFAULT_COLOR,
                      }}
                    />
                    <span className="text-lg font-semibold">{selected.province}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>District Info</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-text-muted">
                Click any district on the map to see its details here.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
