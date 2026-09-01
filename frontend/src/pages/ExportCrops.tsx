import { useQuery } from "@tanstack/react-query";
import { getExportCrops } from "@/lib/api";
import { useFilterStore } from "@/hooks/useFilters";
import { FilterBar } from "@/components/FilterBar";
import { TableSkeleton } from "@/components/Loading";
import { formatNumber } from "@/lib/utils";

export function ExportCrops() {
  const { selectedDistrict } = useFilterStore();

  const {
    data: exportData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["export-crops", selectedDistrict],
    queryFn: () => getExportCrops(selectedDistrict ?? 1),
    enabled: !!selectedDistrict,
    staleTime: 300000,
  });

  if (!selectedDistrict) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} showYearRange={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Select a district to view export crop data.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} showYearRange={false} />
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Could not load export crop data.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading || !exportData) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector={false} showYearRange={false} />
        <TableSkeleton rows={5} />
      </div>
    );
  }

  const exportCrops = exportData.export_crops || [];
  const districtName = exportData.district_name || "Unknown District";

  const totalRevenue = exportCrops.reduce(
    (sum: number, c: any) => sum + (c.estimated_revenue_usd || 0),
    0,
  );

  const stats = [
    {
      label: "Total Export Revenue (USD)",
      value: `$${formatNumber(totalRevenue)}`,
    },
    {
      label: "Number of Export Crops",
      value: exportCrops.length,
    },
    {
      label: "Average Yield (kg/ha)",
      value:
        exportCrops.length > 0
          ? formatNumber(
              exportCrops.reduce(
                (sum: number, c: any) => sum + (c.yield_kg_ha || 0),
                0,
              ) / exportCrops.length,
            )
          : "-",
    },
  ];

  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Export Crops</h1>
      </div>

      <FilterBar showCropSelector={false} showYearRange={false} />

      <p className="text-sm text-text-secondary mb-4">
        Showing export crop analysis for {districtName}
      </p>

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

      <div className="bg-white border border-border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Export Crop Details</h3>
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left p-2 font-medium">Crop</th>
              <th className="text-left p-2 font-medium">Production (MT)</th>
              <th className="text-left p-2 font-medium">Area (ha)</th>
              <th className="text-left p-2 font-medium">Yield (kg/ha)</th>
              <th className="text-left p-2 font-medium">Est. Revenue (USD)</th>
            </tr>
          </thead>
          <tbody>
            {exportCrops.map((item: any, idx: number) => (
              <tr
                key={item.crop_id || idx}
                className="border-b border-border-light"
              >
                <td className="p-2 font-medium">{item.crop_name}</td>
                <td className="p-2">
                  {formatNumber(item.production_mt || 0)} MT
                </td>
                <td className="p-2">
                  {formatNumber(item.area_harvested_ha || 0)} ha
                </td>
                <td className="p-2">
                  {item.yield_kg_ha != null
                    ? `${formatNumber(item.yield_kg_ha)} kg/ha`
                    : "-"}
                </td>
                <td className="p-2">
                  {item.estimated_revenue_usd != null
                    ? `${formatNumber(item.estimated_revenue_usd)}`
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
