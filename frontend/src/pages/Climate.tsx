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
    refetch,
  } = useQuery({
    queryKey: ["climate", selectedDistrict],
    queryFn: () => getClimate(selectedDistrict!),
    enabled: !!selectedDistrict,
  });

  if (error) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {"// Could not load climate data. — "}
            <button
              type="button"
              onClick={() => refetch()}
              className="underline hover:text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              [ RETRY ]
            </button>
          </p>
        </div>
      </div>
    );
  }

  if (!selectedDistrict) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
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
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            Loading climate data...
          </p>
        </div>
      </div>
    );
  }

  const { summary, data } = climateData;

  const monthNames = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  const monthlyAverages = Array.from({ length: 12 }, (_, i) => {
    const rows = data.filter(
      (row: any) =>
        row.observation_date && new Date(row.observation_date).getMonth() === i,
    );
    const avgRain =
      rows.length > 0
        ? rows.reduce((s: number, r: any) => s + (r.rainfall_mm ?? 0), 0) /
          rows.length
        : 0;
    const avgTempMin =
      rows.length > 0
        ? rows.reduce(
            (s: number, r: any) => s + (r.temperature_min_c ?? 0),
            0,
          ) / rows.length
        : 0;
    const avgTempMax =
      rows.length > 0
        ? rows.reduce(
            (s: number, r: any) => s + (r.temperature_max_c ?? 0),
            0,
          ) / rows.length
        : 0;
    const avgSolar =
      rows.length > 0
        ? rows.reduce(
            (s: number, r: any) => s + (r.solar_radiation_mj_m2 ?? 0),
            0,
          ) / rows.length
        : 0;
    return {
      month: monthNames[i],
      rainfall_mm: Math.round(avgRain * 10) / 10,
      temp_min: Math.round(avgTempMin * 10) / 10,
      temp_max: Math.round(avgTempMax * 10) / 10,
      solar: Math.round(avgSolar * 10) / 10,
    };
  });

  const startMonthName =
    summary?.monsoon_start_month != null
      ? monthNames[summary.monsoon_start_month - 1]
      : "Jun";
  const endMonthName =
    summary?.monsoon_end_month != null
      ? monthNames[summary.monsoon_end_month - 1]
      : "Sep";
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
        "Observation Date",
        "Rainfall (mm)",
        "Temperature Min (°C)",
        "Temperature Max (°C)",
        "Temperature Mean (°C)",
        "Solar Radiation (MJ/m²)",
        "Data Source",
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
      downloadBlob(
        new Blob([csvContent], { type: "text/csv" }),
        `climate_${selectedDistrict}.csv`,
      );
    } catch (err) {
      console.error("Failed to download climate CSV:", err);
      alert("Failed to download climate data. Please try again.");
    }
  };

  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">
          Climate Intelligence
        </h1>
        <button
          className="px-4 py-2 border border-border font-mono text-xs uppercase tracking-widest hover:bg-bg-secondary"
          onClick={downloadClimateCsv}
        >
          Download CSV
        </button>
      </div>
      <FilterBar showCropSelector={false} />
      <div className="ruled-grid grid-cols-1 md:grid-cols-3 mb-6">
        {stats.map((stat) => (
          <div key={stat.label} className="p-4 text-center">
            <p className="caption">{stat.label}</p>
            <p className="metric text-lg mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="border border-border p-4 mb-6">
        <h3 className="font-mono text-xs uppercase tracking-widest mb-4">
          Monthly Rainfall
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyAverages}>
            <CartesianGrid
              stroke="var(--color-grid)"
              strokeDasharray="0"
              vertical={false}
            />
            <XAxis
              dataKey="month"
              stroke="var(--color-axis)"
              fontSize={11}
              fontFamily="var(--font-family-mono)"
              tickLine={false}
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
            />
            <Legend
              wrapperStyle={{
                fontFamily: "var(--font-family-mono)",
                fontSize: 11,
                textTransform: "uppercase",
                letterSpacing: ".06em",
              }}
            />
            <Bar
              dataKey="rainfall_mm"
              name="Rainfall (mm)"
              fill="var(--color-text-primary)"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="border border-border p-4 mb-6">
        <h3 className="font-mono text-xs uppercase tracking-widest mb-4">
          Monthly Temperature
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthlyAverages}>
            <CartesianGrid
              stroke="var(--color-grid)"
              strokeDasharray="0"
              vertical={false}
            />
            <XAxis
              dataKey="month"
              stroke="var(--color-axis)"
              fontSize={11}
              fontFamily="var(--font-family-mono)"
              tickLine={false}
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
              dataKey="temp_min"
              name="Min Temp (°C)"
              stroke="var(--color-data-climate)"
              strokeWidth={2}
              dot={false}
              connectNulls
            />
            <Line
              type="monotone"
              dataKey="temp_max"
              name="Max Temp (°C)"
              stroke="var(--color-accent)"
              strokeWidth={2}
              dot={false}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="border border-border p-4">
        <h3 className="font-mono text-xs uppercase tracking-widest mb-4">
          Monthly Solar Radiation
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={monthlyAverages}>
            <CartesianGrid
              stroke="var(--color-grid)"
              strokeDasharray="0"
              vertical={false}
            />
            <XAxis
              dataKey="month"
              stroke="var(--color-axis)"
              fontSize={11}
              fontFamily="var(--font-family-mono)"
              tickLine={false}
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
            />
            <Legend
              wrapperStyle={{
                fontFamily: "var(--font-family-mono)",
                fontSize: 11,
                textTransform: "uppercase",
                letterSpacing: ".06em",
              }}
            />
            <Area
              type="monotone"
              dataKey="solar"
              name="Solar (MJ/m²)"
              stroke="var(--color-text-primary)"
              fill="var(--color-text-primary)"
              fillOpacity={0.08}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
