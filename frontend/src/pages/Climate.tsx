import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Bar,
  BarChart,
  Area,
  AreaChart,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { useFilterStore } from "@/hooks/useFilters";
import { formatNumber } from "@/lib/utils";
import { FilterBar } from "@/components/FilterBar";
import { getClimate } from "@/lib/api";
import { downloadBlob } from "@/lib/utils";

export function Climate() {
  const { selectedDistrict } = useFilterStore();

  const {
    data: climateData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["climate", selectedDistrict],
    queryFn: () => getClimate(selectedDistrict!),
    enabled: !!selectedDistrict,
  });

  if (error) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">Could not load climate data.</p>
        </div>
      </div>
    );
  }

  if (!selectedDistrict) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Select a district to view climate data.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading || !climateData) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">Loading climate data...</p>
        </div>
      </div>
    );
  }

  const { summary, data } = climateData;

  const monthNames = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];

  // Group raw monthly rows by calendar month and average
  const monthlyAverages = Array.from({ length: 12 }, (_, i) => {
    const rows = data.filter(
      (row: any) => row.observation_date && new Date(row.observation_date).getMonth() === i,
    );
    const avgRain = rows.length > 0
      ? rows.reduce((s: number, r: any) => s + (r.rainfall_mm ?? 0), 0) / rows.length
      : 0;
    const avgTempMin = rows.length > 0
      ? rows.reduce((s: number, r: any) => s + (r.temperature_min_c ?? 0), 0) / rows.length
      : 0;
    const avgTempMax = rows.length > 0
      ? rows.reduce((s: number, r: any) => s + (r.temperature_max_c ?? 0), 0) / rows.length
      : 0;
    const avgSolar = rows.length > 0
      ? rows.reduce((s: number, r: any) => s + (r.solar_radiation_mj_m2 ?? 0), 0) / rows.length
      : 0;
    return {
      month: monthNames[i],
      rainfall_mm: Math.round(avgRain * 10) / 10,
      temp_min: Math.round(avgTempMin * 10) / 10,
      temp_max: Math.round(avgTempMax * 10) / 10,
      solar: Math.round(avgSolar * 10) / 10,
    };
  });

  const startMonthName = summary?.monsoon_start_month != null
    ? monthNames[summary.monsoon_start_month - 1] : "Jun";
  const endMonthName = summary?.monsoon_end_month != null
    ? monthNames[summary.monsoon_end_month - 1] : "Sep";
  const monsoonPeriod = `${startMonthName}–${endMonthName}`;

  const stats = [
    {
      label: "Annual Rainfall",
      value:
        summary?.annual_rainfall_mm != null
          ? `${formatNumber(summary.annual_rainfall_mm, 1)} mm`
          : "-",
    },
    {
      label: "Avg Temperature",
      value:
        summary?.avg_temperature_c != null
          ? `${formatNumber(summary.avg_temperature_c, 1)}°C`
          : "-",
    },
    {
      label: "Monsoon Period",
      value: monsoonPeriod,
    },
  ];

  const downloadClimateCsv = async () => {
    if (!climateData) return;
    try {
      const header = [
        "Observation Date", "Rainfall (mm)",
        "Temperature Min (°C)", "Temperature Max (°C)",
        "Temperature Mean (°C)", "Solar Radiation (MJ/m²)", "Data Source",
      ];
      const rows = data.map((row: any) => [
        row.observation_date,
        row.rainfall_mm ?? "",
        row.temperature_min_c ?? "",
        row.temperature_max_c ?? "",
        row.temperature_mean_c ?? "",
        row.solar_radiation_mj_m2 ?? "",
        row.data_source ?? "",
      ]);
      const csvContent = [header, ...rows]
        .map((r: any[]) => r.map((v: string) => `"${v}"`).join(","))
        .join("\n");
      downloadBlob(new Blob([csvContent], { type: "text/csv" }), `climate_${selectedDistrict}.csv`);
    } catch (err) {
      console.error("Failed to download climate CSV:", err);
      alert("Failed to download climate data. Please try again.");
    }
  };

  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Climate Intelligence</h1>
        <button
          className="px-4 py-2 border border-border rounded-md text-sm hover:bg-bg-tertiary"
          onClick={downloadClimateCsv}
        >
          Download CSV
        </button>
      </div>
      <FilterBar showCropSelector={false} />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-white border border-border rounded-lg p-4"
          >
            <p className="text-sm text-text-secondary">{stat.label}</p>
            <p className="text-2xl font-bold mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Monthly Rainfall Chart */}
      <div className="bg-white border border-border rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold mb-4">Monthly Rainfall</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyAverages}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
            <XAxis dataKey="month" stroke="var(--color-text-muted)" fontSize={12} />
            <YAxis stroke="var(--color-text-muted)" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--color-bg-primary)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-md)",
              }}
            />
            <Legend />
            <Bar
              dataKey="rainfall_mm"
              name="Rainfall (mm)"
              fill="var(--color-primary)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Temperature Chart — dual line (min/max) */}
      <div className="bg-white border border-border rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold mb-4">Monthly Temperature</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthlyAverages}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
            <XAxis dataKey="month" stroke="var(--color-text-muted)" fontSize={12} />
            <YAxis stroke="var(--color-text-muted)" fontSize={12} />
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
              dataKey="temp_min"
              name="Min Temp (°C)"
              stroke="var(--color-secondary)"
              strokeWidth={2}
              connectNulls
            />
            <Line
              type="monotone"
              dataKey="temp_max"
              name="Max Temp (°C)"
              stroke="var(--color-warning)"
              strokeWidth={2}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Solar Radiation Chart */}
      <div className="bg-white border border-border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Monthly Solar Radiation</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={monthlyAverages}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
            <XAxis dataKey="month" stroke="var(--color-text-muted)" fontSize={12} />
            <YAxis stroke="var(--color-text-muted)" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--color-bg-primary)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-md)",
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="solar"
              name="Solar (MJ/m²)"
              stroke="var(--color-chart-3)"
              fill="var(--color-chart-3)"
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
