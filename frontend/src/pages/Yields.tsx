import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Button } from "@/shadcn/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";
import { formatNumber } from "@/lib/utils";
import { getYields, downloadYieldsCsv } from "@/lib/api";
import type { YieldRecord } from "@/lib/types";
import { useFilterStore } from "@/hooks/useFilters";
import { FilterBar } from "@/components/FilterBar";
import { downloadBlob } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";

// ponytail: extracted from 4 duplicate early-return blocks — each shares the
// same header + FilterBar shell, only the message differs.
function StateShell({ message }: { message: string }) {
  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Yield Analysis</h1>
      </div>
      <FilterBar showCropSelector showYearRange />
      <div className="text-center py-12">
        <p className="text-text-secondary">{message}</p>
      </div>
    </div>
  );
}

export function Yields() {
  const { selectedDistrict, selectedCrop, yearStart, yearEnd } =
    useFilterStore();

  const {
    data: yieldsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["yields", selectedDistrict, selectedCrop, yearStart, yearEnd],
    queryFn: () =>
      getYields(
        selectedDistrict!,
        selectedCrop!,
        yearStart || undefined,
        yearEnd || undefined,
      ),
    enabled: !!selectedDistrict && !!selectedCrop,
    staleTime: 300000,
  });

  if (error) {
    return <StateShell message="Could not load yield data." />;
  }

  if (!selectedDistrict || !selectedCrop) {
    return (
      <StateShell message="Select a district and crop to view yield trends." />
    );
  }

  if (isLoading && yieldsData === undefined) {
    return <StateShell message="Loading yield data..." />;
  }

  if (!yieldsData) {
    return (
      <StateShell message="No yield data available for the selected filters." />
    );
  }

  const { timeseries, statistics, district_name, crop_name } = yieldsData;

  const chartData = timeseries.map((t: YieldRecord) => ({
    year: t.year,
    yield: t.yield_kg_ha,
    production: t.production_mt,
  }));

  const downloadYields = async () => {
    try {
      const blob = await downloadYieldsCsv({
        district_id: selectedDistrict,
        crop_id: selectedCrop,
        year_start: yearStart,
        year_end: yearEnd,
      });
      downloadBlob(blob, `yields_${district_name}_${crop_name}.csv`);
    } catch (err) {
      console.error("Download failed:", err);
      alert("Failed to download CSV. Please try again.");
    }
  };

  const stats = [
    {
      label: "Average Yield",
      value:
        statistics?.avg_yield_kg_ha != null
          ? `${formatNumber(statistics.avg_yield_kg_ha)} kg/ha`
          : "-",
    },
    {
      label: "Highest",
      value:
        statistics?.max_yield_kg_ha != null
          ? `${formatNumber(statistics.max_yield_kg_ha)} kg/ha`
          : "-",
    },
    {
      label: "Lowest",
      value:
        statistics?.min_yield_kg_ha != null
          ? `${formatNumber(statistics.min_yield_kg_ha)} kg/ha`
          : "-",
    },
    {
      label: "Volatility (σ)",
      value:
        statistics?.volatility != null
          ? `${formatNumber(statistics.volatility)} kg/ha`
          : "-",
    },
  ];

  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Yield Analysis</h1>
        <Button variant="outline" onClick={downloadYields}>
          Export CSV
        </Button>
      </div>
      <FilterBar showCropSelector showYearRange />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="pt-6">
              <p className="text-sm text-text-secondary">{stat.label}</p>
              <p className="text-2xl font-bold mt-1">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>
            {crop_name} — {district_name} Yield Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border-light)"
              />
              <XAxis
                dataKey="year"
                stroke="var(--color-text-muted)"
                fontSize={12}
              />
              <YAxis
                stroke="var(--color-text-muted)"
                fontSize={12}
                tickFormatter={(v) => formatNumber(v)}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-bg-primary)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "var(--radius-md)",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="yield"
                stroke="var(--color-primary)"
                strokeWidth={2}
                name="Yield (kg/ha)"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
