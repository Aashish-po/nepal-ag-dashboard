import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/shadcn/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";
import { getCommercialization, getCommercializationList } from "@/lib/api";
import { useFilterStore } from "@/hooks/useFilters";
import { FilterBar } from "@/components/FilterBar";
import { TableSkeleton } from "@/components/Loading";
import { formatNumber } from "@/lib/utils";

export function Commercialization() {
  const { selectedDistrict, yearEnd, setSelectedDistrict } = useFilterStore();
  const year = yearEnd || 2024;

  const {
    data: heatmapData,
    isLoading: heatmapLoading,
    error: heatmapError,
    refetch: refetchHeatmap,
  } = useQuery({
    queryKey: ["commercialization-list", year],
    queryFn: () => getCommercializationList(year),
    staleTime: 300000,
  });

  const {
    data: districtDetail,
    error: detailError,
    refetch: refetchDetail,
  } = useQuery({
    queryKey: ["commercialization-detail", selectedDistrict, year],
    queryFn: () => getCommercialization(selectedDistrict!, year),
    enabled: !!selectedDistrict,
    staleTime: 300000,
  });

  if (detailError) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {"// Could not load commercialization data. — "}
            <button
              type="button"
              onClick={() => refetchDetail()}
              className="underline hover:text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              [ RETRY ]
            </button>
          </p>
        </div>
      </div>
    );
  }

  if (heatmapError) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {"// Could not load commercialization rankings. — "}
            <button
              type="button"
              onClick={() => refetchHeatmap()}
              className="underline hover:text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              [ RETRY ]
            </button>
          </p>
        </div>
      </div>
    );
  }

  if (heatmapLoading || !heatmapData) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <TableSkeleton rows={5} />
      </div>
    );
  }

  const heatmapRows = (heatmapData.districts || [])
    .map((d: any) => ({
      district: d.district_name || d.name,
      province: d.province,
      score: d.commercialization_score,
      exportArea: d.export_crop_area_pct,
      subsistence: d.subsistence_area_pct,
      holdingSize: d.avg_holding_size_ha,
    }))
    .filter((row: any) => row.score != null)
    .sort((a: any, b: any) => (b.score ?? -Infinity) - (a.score ?? -Infinity));

  const provincialMap = heatmapRows.reduce((acc: any, row: any) => {
    const prov = row.province || "Unknown";
    if (!acc[prov]) acc[prov] = [];
    acc[prov].push(row.score);
    return acc;
  }, {});

  const provincialData = (
    Object.entries(provincialMap) as [string, number[]][]
  ).map(([province, scores]) => ({
    province,
    score: scores.reduce((a: number, b: number) => a + b, 0) / scores.length,
  }));

  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">
          Commercialization Dashboard
        </h1>
      </div>

      <FilterBar showCropSelector={false} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-0 border border-border mb-6">
        <Card className="lg:col-span-2 border-0 border-r border-border">
          <CardHeader>
            <CardTitle>Commercialization Scores by District</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={heatmapRows} layout="vertical">
                <CartesianGrid
                  stroke="var(--color-grid)"
                  strokeDasharray="0"
                  vertical={false}
                />
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  stroke="var(--color-axis)"
                  fontSize={11}
                  fontFamily="var(--font-family-mono)"
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="district"
                  stroke="var(--color-axis)"
                  fontSize={11}
                  fontFamily="var(--font-family-mono)"
                  tickLine={false}
                  width={100}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-bg-primary)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "0",
                    fontFamily: "var(--font-family-mono)",
                    fontSize: "11px",
                    textTransform: "uppercase",
                  }}
                />
                <Bar
                  dataKey="score"
                  name="Score"
                  fill="var(--color-text-primary)"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-0">
          <CardHeader>
            <CardTitle>Provincial Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={provincialData}>
                <CartesianGrid
                  stroke="var(--color-grid)"
                  strokeDasharray="0"
                  vertical={false}
                />
                <XAxis
                  dataKey="province"
                  stroke="var(--color-axis)"
                  fontSize={11}
                  fontFamily="var(--font-family-mono)"
                  tickLine={false}
                  axisLine={{ stroke: "var(--color-border-light)" }}
                />
                <YAxis
                  domain={[0, 100]}
                  stroke="var(--color-axis)"
                  fontSize={11}
                  fontFamily="var(--font-family-mono)"
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-bg-primary)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "0",
                    fontFamily: "var(--font-family-mono)",
                    fontSize: "11px",
                    textTransform: "uppercase",
                  }}
                />
                <Bar
                  dataKey="score"
                  fill="var(--color-accent)"
                  name="Avg Score"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {districtDetail && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>{districtDetail.district_name} Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="ruled-grid grid-cols-2 md:grid-cols-4">
              <div className="p-4 text-center">
                <p className="caption">Score</p>
                <p className="metric text-lg mt-1">
                  {districtDetail.commercialization_score} / 100
                </p>
              </div>
              <div className="p-4 text-center">
                <p className="caption">Export Area</p>
                <p className="metric text-lg mt-1">
                  {formatNumber(districtDetail.export_crop_area_pct ?? 0)}%
                </p>
              </div>
              <div className="p-4 text-center">
                <p className="caption">Subsistence Area</p>
                <p className="metric text-lg mt-1">
                  {formatNumber(districtDetail.subsistence_area_pct ?? 0)}%
                </p>
              </div>
              <div className="p-4 text-center">
                <p className="caption">Avg Holding Size</p>
                <p className="metric text-lg mt-1">
                  {formatNumber(districtDetail.avg_holding_size_ha ?? 0)} ha
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => setSelectedDistrict(null)}
            >
              Close
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
