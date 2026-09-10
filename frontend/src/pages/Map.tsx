import { useMemo, useState } from "react";
import { MapPin, X } from "lucide-react";
import { Button } from "@/shadcn/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";
import nepalGeoJSON from "@/data/nepal_districts.json";
import type { FeatureCollection } from "geojson";
import * as d3Geo from "d3-geo";

const PROVINCE_COLORS: Record<string, string> = {
  Koshi: "#050505",
  Madhesh: "#444444",
  Bagmati: "#8A8580",
  Gandaki: "#2E7D32",
  Lumbini: "#1976D2",
  Karnali: "#00796B",
  Sudurpashchim: "#E61919",
};

const DEFAULT_COLOR = "#C2BEB6";

export interface DistrictInfo {
  id: number;
  uid: string;
  name: string;
  province: string;
  region: string;
  population: number | null;
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
  const [hoveredUid, setHoveredUid] = useState<string | null>(null);

  const { viewBox, paths, circles } = useMemo(() => {
    try {
      const collection = nepalGeoJSON as FeatureCollection;
      // ponytail: filter before fitSize — wrapper id 0 "Nepal" otherwise
      // bloats the bounds and shrinks every district. Keep predicate in
      // one place so render and projection share it.
      const isDistrictFeature = (props: Record<string, unknown>) => {
        if (props.district_name == null && props.name == null) return false;
        if (
          String(props.district_name ?? "")
            .trim()
            .toLowerCase() === "nepal"
        )
          return false;
        if (!Number(props.id ?? 0)) return false;
        if (!props.province) return false;
        return true;
      };
      const filteredFeatures = collection.features.filter((f) =>
        isDistrictFeature((f.properties ?? {}) as Record<string, unknown>),
      );
      const filtered = {
        type: "FeatureCollection",
        features: filteredFeatures,
      } as unknown as FeatureCollection;
      const proj = d3Geo.geoMercator();
      proj.fitSize([800, 500], filtered);
      const geoPath = d3Geo.geoPath(proj);
      const bounds = geoPath.bounds(filtered);
      const pad = 8;
      const vb = {
        x: bounds[0][0] - pad,
        y: bounds[0][1] - pad,
        w: bounds[1][0] - bounds[0][0] + pad * 2,
        h: bounds[1][1] - bounds[0][1] + pad * 2,
      };

      const districtPaths: DistrictPath[] = [];
      const districtCircles: DistrictCircle[] = [];
      for (const feature of filteredFeatures) {
        const props = (feature.properties ?? {}) as Record<string, unknown>;
        const rawId = Number(props.id ?? 0);
        const name = String(props.district_name ?? props.name ?? "Unknown");
        const province = String(props.province ?? "Unknown");
        // ponytail: validate before coerce — 0 is implausible for Nepal
        // districts, so treat null/0/NaN as missing and render "—".
        const popRaw = Number(
          props.census_2021_population ?? props.population,
        );
        const population =
          Number.isFinite(popRaw) && popRaw > 0 ? popRaw : null;
        const district: DistrictInfo = {
          id: rawId || 0,
          uid: rawId ? String(rawId) : `${name}__${province}`,
          name,
          province,
          region: String(props.region ?? "Unknown"),
          population,
          area_sq_km: Number(props.area_sq_km ?? 0),
        };
        if (!feature.geometry) continue;
        const color = PROVINCE_COLORS[district.province] ?? DEFAULT_COLOR;
        const geomType = feature.geometry.type;
        if (geomType === "Polygon" || geomType === "MultiPolygon") {
          const d = geoPath(feature as never);
          if (!d) continue;
          // ponytail: reject giant polygons — a single bogus feature with
          // screen-space coords would otherwise cover the viewBox.
          const fb = geoPath.bounds(feature as never);
          const w = fb[1][0] - fb[0][0];
          const h = fb[1][1] - fb[0][1];
          // ponytail: global viewBox-relative threshold; per-feature area
          // check if Nepal's aspect ratio ever changes.
          if (w > vb.w * 0.6 || h > vb.h * 0.6) {
            console.warn("Suspicious feature skipped:", district.name, {
              w,
              h,
            });
            continue;
          }
          districtPaths.push({ d, district, color });
          continue;
        }
        if (geomType === "Point") {
          const point = proj(
            feature.geometry.coordinates as [number, number],
          );
          if (point) {
            const [cx, cy] = point;
            districtCircles.push({ cx, cy, district, color });
          }
        }
      }

      return {
        viewBox: `${vb.x} ${vb.y} ${vb.w} ${vb.h}`,
        paths: districtPaths,
        circles: districtCircles,
      };
    } catch (err) {
      console.error("Map rendering failed:", err);
      return { viewBox: "0 0 800 500", paths: [], circles: [] };
    }
  }, []);

  const hasData = paths.length > 0 || circles.length > 0;

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">
          District Map
        </h1>
        <span className="hidden sm:inline font-mono text-[10px] uppercase tracking-widest border border-border px-2 py-1">
          77 DISTS - CLICK TO SELECT
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-0 border border-border">
        <div className="border-r border-border">
          <div className="p-4 border-b border-border-light">
            <p className="font-mono text-xs uppercase tracking-widest font-bold">
              Nepal Districts
            </p>
            <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mt-1">
              Ink choropleth - province tint at 18% / hover 30% / selected ink
              reversed
            </p>
          </div>
          <div className="p-4">
            <div className="w-full overflow-x-auto border border-border-light p-2 bg-bg-primary">
              {!hasData ? (
                <div className="p-8 text-center">
                  <p className="font-mono text-xs uppercase tracking-widest text-text-error">
                    Failed to load district map.
                  </p>
                  <p className="font-mono text-[10px] mt-2 text-text-muted">
                    Check console for details.
                  </p>
                </div>
              ) : (
                <svg
                  viewBox={viewBox}
                  preserveAspectRatio="xMidYMid meet"
                  className="w-full h-auto"
                  style={{ display: "block", maxWidth: "50rem" }}
                  role="img"
                  aria-label="Choropleth map of Nepal districts by province"
                >
                  {paths.map(({ d, district, color }) => {
                    const isActive = selected?.uid === district.uid;
                    const isHovered = hoveredUid === district.uid;
                    return (
                      <g
                        key={`path-${district.uid}`}
                        onMouseEnter={() => setHoveredUid(district.uid)}
                        onMouseLeave={() => setHoveredUid(null)}
                        onFocus={() => setHoveredUid(district.uid)}
                        onBlur={() => setHoveredUid(null)}
                        onClick={() =>
                          setSelected((prev) =>
                            prev?.uid === district.uid ? null : district,
                          )
                        }
                        tabIndex={0}
                        role="button"
                        aria-pressed={isActive}
                        aria-label={`${district.name} district${isActive ? " selected" : ""}`}
                        className="cursor-pointer focus-visible:outline-2 focus-visible:outline-[#E61919] focus-visible:outline-offset-2"
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            setSelected((prev) =>
                              prev?.uid === district.uid ? null : district,
                            );
                          }
                        }}
                      >
                        <title>{district.name}</title>
                        <path
                          d={d}
                          fill={
                            isActive
                              ? "#050505"
                              : isHovered
                                ? color === "#050505"
                                  ? "#1a1a1a"
                                  : color
                                : color
                          }
                          fillOpacity={isActive ? 1 : isHovered ? 0.3 : 0.18}
                          stroke={isActive ? "#E61919" : color}
                          strokeWidth={isActive ? 2 : 1}
                          style={{
                            transition: "fill 0.15s, fill-opacity 0.15s",
                          }}
                        />
                      </g>
                    );
                  })}
                  {circles.map(({ cx, cy, district, color }) => {
                    const isActive = selected?.uid === district.uid;
                    const isHovered = hoveredUid === district.uid;
                    const size = isActive ? 6 : 4;
                    return (
                      <g
                        key={`circle-${district.uid}`}
                        onMouseEnter={() => setHoveredUid(district.uid)}
                        onMouseLeave={() => setHoveredUid(null)}
                        onFocus={() => setHoveredUid(district.uid)}
                        onBlur={() => setHoveredUid(null)}
                        onClick={() =>
                          setSelected((prev) =>
                            prev?.uid === district.uid ? null : district,
                          )
                        }
                        tabIndex={0}
                        role="button"
                        aria-pressed={isActive}
                        aria-label={`${district.name} district${isActive ? " selected" : ""}`}
                        className="cursor-pointer focus-visible:outline-2 focus-visible:outline-[#E61919] focus-visible:outline-offset-2"
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            setSelected((prev) =>
                              prev?.uid === district.uid ? null : district,
                            );
                          }
                        }}
                      >
                        <title>{district.name}</title>
                        <rect
                          x={cx - size / 2}
                          y={cy - size / 2}
                          width={size}
                          height={size}
                          fill={
                            isActive
                              ? "#050505"
                              : isHovered
                                ? color === "#050505"
                                  ? "#1a1a1a"
                                  : color
                                : color
                          }
                          fillOpacity={isActive ? 1 : isHovered ? 1 : 0.9}
                          stroke={isActive ? "#E61919" : color}
                          strokeWidth={isActive ? 1.5 : 1}
                          style={{ transition: "fill 0.15s" }}
                        />
                      </g>
                    );
                  })}
                </svg>
              )}
            </div>
            <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mt-3">
              Click to select - ink density = province
            </p>
            <div className="flex flex-wrap gap-3 mt-3 border-t border-border-light pt-3">
              {Object.entries(PROVINCE_COLORS).map(([prov, c]) => (
                <span
                  key={prov}
                  className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-text-secondary"
                >
                  <span
                    className="w-3 h-3 inline-block shrink-0 border border-border"
                    style={{ background: c }}
                  />
                  {prov}
                </span>
              ))}
            </div>
          </div>
        </div>

        {selected ? (
          <Card className="border-0">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base">{selected.name}</CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSelected(null)}
              >
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-text-secondary">
                  <MapPin className="w-4 h-4 shrink-0" />
                  <span>
                    {selected.province} - {selected.region}
                  </span>
                </div>
                <div className="border-t border-border-light pt-3">
                  <p className="caption">Population</p>
                  <p className="metric text-lg mt-1">
                    {selected.population != null
                      ? selected.population.toLocaleString()
                      : "—"}
                  </p>
                </div>
                <div className="border-t border-border-light pt-3">
                  <p className="caption">Area</p>
                  <p className="metric text-lg mt-1">
                    {selected.area_sq_km.toLocaleString()} km²
                  </p>
                </div>
                <div className="border-t border-border-light pt-3">
                  <p className="caption">Province</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className="inline-block w-4 h-4 shrink-0 border border-border"
                      style={{
                        background:
                          PROVINCE_COLORS[selected.province] ?? DEFAULT_COLOR,
                      }}
                    />
                    <span className="font-mono text-xs uppercase tracking-widest font-bold">
                      {selected.province}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-0">
            <CardHeader>
              <CardTitle>District Info</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-mono text-xs uppercase tracking-widest text-text-muted">
                Click any district on the map to see its details here.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
