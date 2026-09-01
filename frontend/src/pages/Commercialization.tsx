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
  const { selectedDistrict, yearEnd, setSelectedDistrict } =
    useFilterStore();
  const year = yearEnd || 2024;

  const {
    data: heatmapData,
    isLoading: heatmapLoading,
    error: heatmapError,
  } = useQuery({
    queryKey: ["commercialization-list", year],
    queryFn: () => getCommercializationList(year),
    staleTime: 300000,
  });

  const { data: districtDetail, error: detailError } = useQuery({
    queryKey: ["commercialization-detail", selectedDistrict, year],
    queryFn: () => getCommercialization(selectedDistrict!, year),
    enabled: !!selectedDistrict,
    staleTime: 300000,
  });

  if (detailError) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Could not load commercialization data.
          </p>
        </div>
      </div>
    );
  }

  if (heatmapError) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Could not load commercialization rankings.
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
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Commercialization Dashboard</h1>
      </div>

      <FilterBar showCropSelector={false} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Commercialization Scores by District</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={heatmapRows} layout="vertical">
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--color-border-light)"
                />
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  stroke="var(--color-text-muted)"
                  fontSize={12}
                />
                <YAxis
                  type="category"
                  dataKey="district"
                  stroke="var(--color-text-muted)"
                  fontSize={12}
                  width={100}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-bg-primary)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-md)",
                  }}
                />
                <Bar
                  dataKey="score"
                  radius={[0, 4, 4, 0]}
                  name="Score"
                  fill="var(--color-primary)"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Provincial Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={provincialData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--color-border-light)"
                />
                <XAxis
                  dataKey="province"
                  stroke="var(--color-text-muted)"
                  fontSize={12}
                />
                <YAxis
                  domain={[0, 100]}
                  stroke="var(--color-text-muted)"
                  fontSize={12}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-bg-primary)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-md)",
                  }}
                />
                <Bar
                  dataKey="score"
                  fill="var(--color-secondary)"
                  radius={[4, 4, 0, 0]}
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
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-text-secondary">Score</p>
                <p className="text-xl font-bold">
                  {districtDetail.commercialization_score} / 100
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Export Area</p>
                <p className="text-xl font-bold">
                  {formatNumber(districtDetail.export_crop_area_pct)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Subsistence Area</p>
                <p className="text-xl font-bold">
                  {formatNumber(districtDetail.subsistence_area_pct)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Avg Holding Size</p>
                <p className="text-xl font-bold">
                  {formatNumber(districtDetail.avg_holding_size_ha)} ha
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
