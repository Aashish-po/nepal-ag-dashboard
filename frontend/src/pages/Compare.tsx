import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/shadcn/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";
import { Table, TableBody, TableRow, TableCell } from "@/shadcn/table";
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
  "var(--color-primary)",
  "var(--color-secondary)",
  "var(--color-warning)",
  "var(--color-error)",
  "var(--color-chart-5)",
];

export function Compare() {
  const { selectedCrop, yearStart, yearEnd, selectedDistricts, setSelectedDistricts } =
    useFilterStore();

  // Multi-select state for district chips (client-side only, synced to store on submit)
  const [draftIds, setDraftIds] = useState<number[]>([]);
  const [showSelector, setShowSelector] = useState(false);

  // Load districts list for selector
  const { data: districtsData } = useQuery({
    queryKey: ["districts"],
    queryFn: () => getDistricts(),
    staleTime: 3600000,
  });
  const allDistricts = districtsData?.districts || [];

  const toggleDraft = (id: number) => {
    setDraftIds(prev => {
      if (prev.includes(id)) return prev.filter(x => x !== id);
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

  // Use store-based selectedDistricts for actual queries
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

  const { data: compareData, isLoading, error } = queries;

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
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Compare Districts</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport} disabled={!compareDistricts.length}>
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

      {/* Multi-district selector modal */}
      {showSelector && (
        <div className="mb-6 bg-white border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">Select Districts to Compare</h3>
            <button
              className="text-xs text-text-secondary hover:text-text-primary"
              onClick={() => setShowSelector(false)}
            >
              ✕
            </button>
          </div>
          <p className="text-xs text-text-muted mb-3">
            Click to select up to {MAX_COMPARE} districts. Selected:{" "}
            {draftIds.length > 0
              ? draftIds.map((id) => allDistricts.find((d: { id: number; name: string }) => d.id === id)?.name).join(", ")
              : "None"}
          </p>
          <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto mb-3">
            {allDistricts.map((d: { id: number; name: string }) => {
              const isSelected = draftIds.includes(d.id);
              return (
                <button
                  key={d.id}
                  className={`px-2 py-1.5 text-xs rounded-md border text-left transition-colors ${
                    isSelected
                      ? "bg-primary text-white border-primary"
                      : "border-border hover:bg-bg-tertiary"
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

      {/* Active comparison chips */}
      {compareDistricts.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {compareDistricts.map((id) => {
            const d = allDistricts.find((dist: { id: number; name: string }) => dist.id === id);
            return (
              <span
                key={id}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-bg-tertiary text-sm"
              >
                {d?.name ?? `ID ${id}`}
                <button
                  className="text-text-muted hover:text-text-primary"
                  onClick={() => setSelectedDistricts(compareDistricts.filter((x) => x !== id))}
                >
                  ✕
                </button>
              </span>
            );
          })}
          {compareDistricts.length > 0 && (
            <button
              className="text-xs text-text-muted hover:text-text-primary underline"
              onClick={clearCompare}
            >
              Clear all
            </button>
          )}
        </div>
      )}

      <FilterBar showCropSelector />

      {!compareDistricts.length ? (
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Select 2–{MAX_COMPARE} districts above to compare yield trends.
          </p>
        </div>
      ) : compareDistricts.length === 1 ? (
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Select at least 2 districts to compare.
          </p>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-text-secondary">Could not load comparison data.</p>
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
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                    <XAxis dataKey="year" stroke="var(--color-text-muted)" fontSize={12} />
                    <YAxis stroke="var(--color-text-muted)" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "var(--color-bg-primary)",
                        border: "1px solid var(--color-border)",
                        borderRadius: "var(--radius-md)",
                      }}
                    />
                    <Legend />
                    {compareData.map((d: any, idx: number) => {
                      const key = d.district_name.replace(/\s+/g, "_").toLowerCase();
                      return (
                        <Line
                          key={key}
                          type="monotone"
                          dataKey={key}
                          stroke={COLORS[idx % COLORS.length]}
                          strokeWidth={2}
                          name={d.district_name}
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
              <Table>
                <TableBody>
                  {statsRows.map((row: any) => (
                    <TableRow key={row.district}>
                      <TableCell className="font-medium">{row.district}</TableCell>
                      <TableCell>{row.avg} kg/ha</TableCell>
                      <TableCell>{row.max} kg/ha</TableCell>
                      <TableCell>{row.volatility} kg/ha</TableCell>
                      <TableCell>{row.cagr}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
