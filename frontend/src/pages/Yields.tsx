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

function StateShell({
  message,
  actionLabel,
  onAction,
}: {
  message: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">
          Yield Analysis
        </h1>
      </div>
      <FilterBar showCropSelector showYearRange />
      <div className="text-center py-12 border border-border">
        <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
          {message}
          {actionLabel && onAction ? (
            <>
              {" — "}
              <button
                type="button"
                onClick={onAction}
                className="underline hover:text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
              >
                [ {actionLabel} ]
              </button>
            </>
          ) : null}
        </p>
      </div>
    </div>
  );
}

export function Yields() {
  const { selectedDistrict, selectedCrop, yearStart, yearEnd, reset } =
    useFilterStore();

  const {
    data: yieldsData,
    isLoading,
    error,
    refetch,
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
    return (
      <StateShell
        message="Could not load yield data."
        actionLabel="RETRY"
        onAction={() => refetch()}
      />
    );
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
      <StateShell
        message="No yield data available for the selected filters."
        actionLabel="CLEAR FILTERS"
        onAction={() => reset()}
      />
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
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">
          Yield Analysis
        </h1>
        <Button variant="outline" onClick={downloadYields}>
          Export CSV
        </Button>
      </div>
      <FilterBar showCropSelector showYearRange />

      <div className="ruled-grid grid-cols-1 md:grid-cols-4 mb-6">
        {stats.map((stat) => (
          <div key={stat.label} className="p-4 text-center">
            <p className="caption">{stat.label}</p>
            <p className="metric mt-1 text-lg">{stat.value}</p>
          </div>
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
                stroke="var(--color-grid)"
                strokeDasharray="0"
                vertical={false}
              />
              <XAxis
                dataKey="year"
                stroke="var(--color-axis)"
                fontSize={11}
                fontFamily="var(--font-family-mono)"
                tickLine={false}
                axisLine={{ stroke: "var(--color-border-light)" }}
              />
              <YAxis
                stroke="var(--color-axis)"
                fontSize={11}
                fontFamily="var(--font-family-mono)"
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => formatNumber(v)}
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
                cursor={{
                  stroke: "var(--color-accent)",
                  strokeWidth: 1,
                  strokeDasharray: "4 4",
                }}
              />
              <Legend
                wrapperStyle={{
                  fontFamily: "var(--font-family-mono)",
                  fontSize: 11,
                  textTransform: "uppercase",
                  letterSpacing: ".06em",
                }}
              />
              <Line
                type="monotone"
                dataKey="yield"
                stroke="var(--color-text-primary)"
                strokeWidth={2}
                name="Yield (kg/ha)"
                dot={false}
                activeDot={{ r: 0 } as any}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
