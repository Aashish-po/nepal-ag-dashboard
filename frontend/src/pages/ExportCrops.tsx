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
    refetch,
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
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
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
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {"// Could not load export crop data. — "}
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
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">
          Export Crops
        </h1>
      </div>

      <FilterBar showCropSelector={false} showYearRange={false} />

      <p className="font-mono text-xs uppercase tracking-widest text-text-secondary mb-4 border border-border-light px-2 py-1 inline-block">
        Showing export crop analysis for {districtName}
      </p>

      <div className="ruled-grid grid-cols-1 md:grid-cols-3 mb-6">
        {stats.map((stat) => (
          <div key={stat.label} className="p-4 text-center">
            <p className="caption">{stat.label}</p>
            <p className="metric text-lg mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="border border-border p-4">
        <h3 className="font-mono text-xs uppercase tracking-widest mb-4">
          Export Crop Details
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-border">
                <th className="text-left p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Crop
                </th>
                <th className="text-right p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Production (MT)
                </th>
                <th className="text-right p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Area (ha)
                </th>
                <th className="text-right p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Yield (kg/ha)
                </th>
                <th className="text-right p-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Est. Revenue (USD)
                </th>
              </tr>
            </thead>
            <tbody>
              {exportCrops.map((item: any, idx: number) => (
                <tr
                  key={item.crop_id || idx}
                  className="border-b border-border-light hover:bg-bg-secondary"
                >
                  <td className="p-2 font-mono text-xs uppercase tracking-wider font-bold">
                    {item.crop_name}
                  </td>
                  <td className="p-2 font-mono text-xs text-right tabular-nums">
                    {formatNumber(item.production_mt || 0)} MT
                  </td>
                  <td className="p-2 font-mono text-xs text-right tabular-nums">
                    {formatNumber(item.area_harvested_ha || 0)} ha
                  </td>
                  <td className="p-2 font-mono text-xs text-right tabular-nums">
                    {item.yield_kg_ha != null
                      ? `${formatNumber(item.yield_kg_ha)} kg/ha`
                      : "-"}
                  </td>
                  <td className="p-2 font-mono text-xs text-right tabular-nums">
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
    </div>
  );
}
