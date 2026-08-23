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
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/shadcn/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";
import { Table, TableBody, TableRow, TableCell } from "@/shadcn/table";
import { getYields, downloadYieldsCsv } from "@/lib/api";
import { useFilterStore } from "@/hooks/useFilters";
import { FilterBar } from "@/components/FilterBar";
import { TableSkeleton } from "@/components/Loading";
import { formatNumber } from "@/lib/utils";

export function Compare() {
  const { compareDistricts, selectedCrop, yearStart, yearEnd } =
    useFilterStore();

  const cropId = selectedCrop;

  const queries = useQuery({
    queryKey: ["compare", compareDistricts, cropId, yearStart, yearEnd],
    queryFn: async () => {
      if (!compareDistricts.length || !cropId) return [];
      const results = await Promise.all(
        compareDistricts.map(async (districtId) => {
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
    enabled: compareDistricts.length > 0 && !!cropId,
    staleTime: 300000,
  });

  const { data: compareData, isLoading, error } = queries;

  if (!compareDistricts.length) {
    return (
      <div className="max-w-[1400px] mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-h1 font-bold">Compare Districts</h1>
          <Button
            variant="outline"
            onClick={() => alert("Export comparison CSV triggered")}
          >
            Export Comparison
          </Button>
        </div>
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Select districts to compare using the sidebar filter.
          </p>
        </div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="max-w-[1400px] mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">Could not load comparison data.</p>
        </div>
      </div>
    )
  }

  if (isLoading || !compareData) {
    return (
      <div className="max-w-[1400px] mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <TableSkeleton rows={5} />
      </div>
    );
  }

  const COLORS = [
    "var(--color-primary)",
    "var(--color-secondary)",
    "var(--color-warning)",
    "var(--color-error)",
    "var(--color-chart-5)",
  ];

  const allYears: number[] = Array.from(
    new Set<number>(compareData.flatMap((d: any) => d.timeseries.map((t: any) => t.year))),
  ).sort((a, b) => a - b);

  const chartData = allYears.map((year) => {
    const row: any = { year };
    compareData.forEach((d: any) => {
      const entry = d.timeseries.find((t: any) => t.year === year);
      const key = d.district_name.replace(/\s+/g, "_").toLowerCase();
      row[key] = entry?.yield_kg_ha || null;
    });
    return row;
  });

  const statsRows = compareData.map((d: any) => ({
    district: d.district_name,
    avg: formatNumber(d.statistics?.avg_yield_kg_ha || 0),
    max: formatNumber(d.statistics?.max_yield_kg_ha || 0),
    volatility: formatNumber(d.statistics?.volatility || 0, 1),
    cagr: formatNumber(d.statistics?.cagr_pct || 0, 1),
  }));

  const handleExport = async () => {
    if (!compareDistricts.length || !cropId) return;
    try {
      // Fetch all district data and merge
      const allData = [];
      for (const districtId of compareDistricts) {
        const blob = await downloadYieldsCsv({
          district_id: districtId,
          crop_id: cropId,
          year_start: yearStart || 2014,
          year_end: yearEnd || 2024,
        });
        // Convert blob to text and parse CSV
        const text = await blob.text();
        const lines = text.trim().split('\n');
        if (allData.length === 0) {
          // Keep header from first district
          allData.push(lines[0]);
        }
        // Add data rows (skip header)
        allData.push(...lines.slice(1));
      }
      
      const csvContent = allData.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `comparison_${compareDistricts.join("_")}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      // Defer revocation until after download starts
      setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export comparison data');
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Compare Districts</h1>
        <Button variant="outline" onClick={handleExport}>
          Export Comparison
        </Button>
      </div>

      <FilterBar showCropSelector={false} />

      {chartData.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Trend Comparison</CardTitle>
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
    </div>
  );
}
