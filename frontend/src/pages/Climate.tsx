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

  const { summary } = climateData;

  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const getMonthName = (month: number | null | undefined): string => {
    if (month == null || month < 1 || month > 12) return "";
    return monthNames[month - 1];
  };

  const startMonthName = getMonthName(summary?.monsoon_start_month);
  const endMonthName = getMonthName(summary?.monsoon_end_month);
  const monsoonPeriod =
    startMonthName && endMonthName
      ? `${startMonthName}–${endMonthName}`
      : "Jun–Sep";

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
    if (!climateData) {
      alert("No climate data available to download.");
      return;
    }
    try {
      const { data } = climateData;
      // Create CSV header
      const header = [
        "Observation Date",
        "Rainfall (mm)",
        "Temperature Min (°C)",
        "Temperature Max (°C)",
        "Temperature Mean (°C)",
        "Solar Radiation (MJ/m²)",
        "Data Source",
      ];
      // Create CSV rows
      const rows = data.map((row: any) => [
        row.observation_date,
        row.rainfall_mm ?? "",
        row.temperature_min_c ?? "",
        row.temperature_max_c ?? "",
        row.temperature_mean_c ?? "",
        row.solar_radiation_mj_m2 ?? "",
        row.data_source ?? "",
      ]);
      // Combine header and rows
      const csvContent = [header, ...rows]
        .map((r) => r.map((v: string) => `"${v}"`).join(","))
        .join("\n");
      const blob = new Blob([csvContent], { type: "text/csv" });
      downloadBlob(blob, `climate_${selectedDistrict}.csv`);
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
      {/* Chart visualizations to be implemented */}
      <div className="bg-white border border-border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Monthly Rainfall Chart</h3>
        <p className="text-text-center py-8">Chart visualization coming soon</p>
      </div>
      <div className="bg-white border border-border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Temperature Chart</h3>
        <p className="text-text-center py-8">Chart visualization coming soon</p>
      </div>
      <div className="bg-white border border-border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Solar Radiation Chart</h3>
        <p className="text-text-center py-8">Chart visualization coming soon</p>
      </div>
    </div>
  );
}
