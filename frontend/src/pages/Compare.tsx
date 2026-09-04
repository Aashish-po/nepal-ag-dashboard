import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/shadcn/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";
import { TableBody, TableRow, TableCell } from "@/shadcn/table";
import { getYields, downloadYieldsCsv } from "@/lib/api";
import { getDistricts } from "@/lib/api";
import { useFilterStore } from "@/hooks/useFilters";
import { FilterBar } from "@/components/FilterBar";
import { TableSkeleton } from "@/components/Loading";
import { formatNumber, downloadBlob } from "@/lib/utils";
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

const MAX_COMPARE = 5;
const COLORS = [
  "var(--color-text-primary)",
  "var(--color-accent)",
  "var(--color-data-yield)",
  "var(--color-data-climate)",
  "var(--color-chart-5)",
];

export function Compare() {
  const {
    selectedCrop,
    yearStart,
    yearEnd,
    selectedDistricts,
    setSelectedDistricts,
  } = useFilterStore();

  const [draftIds, setDraftIds] = useState<number[]>([]);
  const [showSelector, setShowSelector] = useState(false);

  const { data: districtsData } = useQuery({
    queryKey: ["districts"],
    queryFn: () => getDistricts(),
    staleTime: 3600000,
  });
  const allDistricts = districtsData?.districts || [];

  const toggleDraft = (id: number) => {
    setDraftIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= MAX_COMPARE) return prev;
      return [...prev, id];
    });
  };

  const commitCompare = () => {
    if (draftIds.length > 0) {
      setSelectedDistricts(draftIds);
    }
    setShowSelector(false);
  };

  const clearCompare = () => {
    setSelectedDistricts([]);
    setDraftIds([]);
  };

  const compareDistricts = selectedDistricts;
  const cropId = selectedCrop;

  const queries = useQuery({
    queryKey: ["compare", compareDistricts, cropId, yearStart, yearEnd],
    queryFn: async () => {
      if (!compareDistricts.length || !cropId) return [];
      const results = await Promise.all(
        compareDistricts.map(async (districtId: number) => {
          const data = await getYields(
            districtId,
            cropId,
            yearStart || 2014,
            yearEnd || 2024,
          );
          return {
            district_id: districtId,
            district_name: data.district_name,
            timeseries: data.timeseries,
            statistics: data.statistics,
          };
        }),
      );
      return results;
    },
    enabled: compareDistricts.length >= 2 && !!cropId,
    staleTime: 300000,
  });

  const { data: compareData, isLoading, error, refetch } = queries;

  const chartData = useMemo(() => {
    if (!compareData) return [];
    const allYears: number[] = Array.from(
      new Set<number>(
        compareData.flatMap((d: any) => d.timeseries.map((t: any) => t.year)),
      ),
    ).sort((a, b) => a - b);
    return allYears.map((year) => {
      const row: any = { year };
      compareData.forEach((d: any) => {
        const entry = d.timeseries.find((t: any) => t.year === year);
        const key = d.district_name.replace(/\s+/g, "_").toLowerCase();
        row[key] = entry?.yield_kg_ha || null;
      });
      return row;
    });
  }, [compareData]);

  const statsRows = useMemo(() => {
    if (!compareData) return [];
    return compareData.map((d: any) => ({
      district: d.district_name,
      avg: formatNumber(d.statistics?.avg_yield_kg_ha || 0),
      max: formatNumber(d.statistics?.max_yield_kg_ha || 0),
      volatility: formatNumber(d.statistics?.volatility || 0, 1),
      cagr: formatNumber(d.statistics?.cagr_pct || 0, 1),
    }));
  }, [compareData]);

  const handleExport = async () => {
    if (!compareDistricts.length || !cropId) return;
    try {
      const allData: string[] = [];
      for (const districtId of compareDistricts) {
        const blob = await downloadYieldsCsv({
          district_id: districtId,
          crop_id: cropId,
          year_start: yearStart || 2014,
          year_end: yearEnd || 2024,
        });
        const text = await blob.text();
        const lines = text.trim().split("\n");
        if (allData.length === 0) {
          allData.push(lines[0]);
        }
        allData.push(...lines.slice(1));
      }
      const csvContent = allData.join("\n");
      downloadBlob(
        new Blob([csvContent], { type: "text/csv" }),
        `comparison_${compareDistricts.join("_")}.csv`,
      );
    } catch (error) {
      console.error("Export failed:", error);
      alert("Failed to export comparison data");
    }
  };

  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">
          Compare Districts
        </h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleExport}
            disabled={!compareDistricts.length}
          >
            Export Comparison
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowSelector(true)}
            disabled={compareDistricts.length >= MAX_COMPARE}
          >
            {compareDistricts.length > 0
              ? `Select (${compareDistricts.length}/${MAX_COMPARE})`
              : `Select Districts (0/${MAX_COMPARE})`}
          </Button>
        </div>
      </div>

      {showSelector && (
        <div className="mb-6 border border-border p-4">
          <div className="flex items-center justify-between mb-3 border-b border-border-light pb-2">
            <h3 className="font-mono text-xs uppercase tracking-widest font-bold">
              Select Districts to Compare
            </h3>
            <button
              className="font-mono text-xs uppercase tracking-widest text-text-secondary hover:text-text-primary border border-border px-2 py-1"
              onClick={() => setShowSelector(false)}
            >
              ✕
            </button>
          </div>
          <p className="font-mono text-[11px] uppercase tracking-wider text-text-muted mb-3">
            Click to select up to {MAX_COMPARE} districts. Selected:{" "}
            {draftIds.length > 0
              ? draftIds
                  .map(
                    (id) =>
                      allDistricts.find(
                        (d: { id: number; name: string }) => d.id === id,
                      )?.name,
                  )
                  .join(", ")
              : "None"}
          </p>
          <div className="grid grid-cols-3 gap-0 border border-border max-h-48 overflow-y-auto mb-3">
            {allDistricts.map((d: { id: number; name: string }) => {
              const isSelected = draftIds.includes(d.id);
              return (
                <button
                  key={d.id}
                  className={`px-2 py-1.5 font-mono text-xs uppercase tracking-wider text-left border-r border-b border-border transition-colors ${
                    isSelected
                      ? "bg-text-primary text-bg-primary"
                      : "hover:bg-bg-secondary"
                  }`}
                  onClick={() => toggleDraft(d.id)}
                >
                  {d.name}
                </button>
              );
            })}
          </div>
          <div className="flex gap-2 justify-end">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setDraftIds([]);
              }}
            >
              Clear
            </Button>
            <Button size="sm" onClick={commitCompare}>
              Confirm Selection
            </Button>
          </div>
        </div>
      )}

      {compareDistricts.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {compareDistricts.map((id) => {
            const d = allDistricts.find(
              (dist: { id: number; name: string }) => dist.id === id,
            );
            return (
              <span
                key={id}
                className="inline-flex items-center gap-1 px-2 py-1 border border-border font-mono text-xs uppercase tracking-wider"
              >
                {d?.name ?? `ID ${id}`}
                <button
                  className="ml-1 font-mono text-xs hover:text-accent"
                  onClick={() =>
                    setSelectedDistricts(
                      compareDistricts.filter((x) => x !== id),
                    )
                  }
                >
                  ✕
                </button>
              </span>
            );
          })}
          {compareDistricts.length > 0 && (
            <button
              className="font-mono text-[10px] uppercase tracking-widest text-text-muted hover:text-text-primary border border-border px-2 py-1"
              onClick={clearCompare}
            >
              Clear all
            </button>
          )}
        </div>
      )}

      <FilterBar showCropSelector />

      {!compareDistricts.length ? (
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            Select 2–{MAX_COMPARE} districts above to compare yield trends.
          </p>
        </div>
      ) : compareDistricts.length === 1 ? (
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            Select at least 2 districts to compare.
          </p>
        </div>
      ) : error ? (
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {"// Could not load comparison data. - "}
            <button
              type="button"
              onClick={() => refetch()}
              className="underline hover:text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              [ RETRY ]
            </button>
          </p>
        </div>
      ) : isLoading || !compareData ? (
        <TableSkeleton rows={5} />
      ) : (
        <>
          {chartData.length > 0 && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Yield Trend Comparison</CardTitle>
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
                    {compareData.map((d: any, idx: number) => {
                      const key = d.district_name
                        .replace(/\s+/g, "_")
                        .toLowerCase();
                      return (
                        <Line
                          key={key}
                          type="monotone"
                          dataKey={key}
                          stroke={COLORS[idx % COLORS.length]}
                          strokeWidth={2}
                          name={d.district_name}
                          dot={false}
                          connectNulls
                        />
                      );
                    })}
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Stats Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-border">
                      <th className="text-left p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                        District
                      </th>
                      <th className="text-right p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                        Avg (kg/ha)
                      </th>
                      <th className="text-right p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                        Max (kg/ha)
                      </th>
                      <th className="text-right p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                        Volatility
                      </th>
                      <th className="text-right p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                        CAGR %
                      </th>
                    </tr>
                  </thead>
                  <TableBody>
                    {statsRows.map((row: any) => (
                      <TableRow key={row.district}>
                        <TableCell className="font-bold uppercase tracking-wider">
                          {row.district}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {row.avg} kg/ha
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {row.max} kg/ha
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {row.volatility} kg/ha
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {row.cagr}%
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
