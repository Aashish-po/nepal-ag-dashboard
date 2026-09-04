import { useQuery } from "@tanstack/react-query";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";
import { getCorrelation } from "@/lib/api";
import { useFilterStore } from "@/hooks/useFilters";
import { FilterBar } from "@/components/FilterBar";

export function Correlation() {
  const { selectedDistrict, selectedCrop } = useFilterStore();

  const {
    data: correlationData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["correlation", selectedDistrict, selectedCrop],
    queryFn: () => getCorrelation(selectedDistrict!, selectedCrop!),
    enabled: !!selectedDistrict && !!selectedCrop,
    staleTime: 300000,
  });

  if (error) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {"// Could not load correlation data. — "}
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

  if (isLoading || !correlationData) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {isLoading
              ? "Loading correlation data..."
              : "Select a district and crop to view correlation analysis."}
          </p>
        </div>
      </div>
    );
  }
  const { correlations } = correlationData;
  if (!correlations || Object.keys(correlations).length === 0) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {"// No correlation results for this district and crop."}
          </p>
        </div>
      </div>
    );
  }

  const corrRows = Object.entries(correlations).map(
    ([key, val]: [string, any]) => ({
      variable: key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
      coefficient: val?.coefficient ?? 0,
      pValue: val?.p_value ?? 1,
      significant: val?.significant ?? false,
    }),
  );
  return (
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">
          Yield-Climate Correlation
        </h1>
      </div>

      <FilterBar showCropSelector />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-0 border border-border mb-6">
        <Card className="border-0 border-r border-border">
          <CardHeader>
            <CardTitle>Correlation Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {corrRows.map((row) => (
                <div key={row.variable} className="flex items-center gap-4">
                  <div className="w-40 font-mono text-xs uppercase tracking-wider font-medium">
                    {row.variable}
                  </div>
                  <div
                    className="flex-1 h-8 relative overflow-hidden border border-border"
                    style={{
                      backgroundColor:
                        row.coefficient > 0
                          ? "rgba(5, 5, 5, 0.06)"
                          : "rgba(230, 25, 25, 0.08)",
                    }}
                  >
                    <div
                      className="absolute inset-y-0 left-0"
                      style={{
                        width: `${Math.abs(row.coefficient) * 100}%`,
                        backgroundColor:
                          row.coefficient > 0
                            ? "var(--color-text-primary)"
                            : "var(--color-accent)",
                      }}
                    />
                    <span className="absolute inset-0 flex items-center justify-center font-mono text-xs uppercase tracking-wider font-medium">
                      r = {row.coefficient.toFixed(2)}
                    </span>
                  </div>
                  <div className="w-24 text-right font-mono text-xs text-text-secondary">
                    p = {row.pValue.toFixed(3)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-0">
          <CardHeader>
            <CardTitle>Rainfall vs. Yield</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-center py-8">
              <div className="metric">
                {correlations?.rainfall_mm?.coefficient?.toFixed(3) ?? "0.000"}
              </div>
              <p className="caption">Correlation coefficient (r)</p>
              <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted border border-border inline-block px-2 py-1">
                {correlations?.rainfall_mm?.significant
                  ? "Statistically significant"
                  : "Not statistically significant"}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-0 border-t border-border border-r">
          <CardHeader>
            <CardTitle>Temperature vs. Yield</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-center py-8">
              <div className="metric">
                {correlations?.temperature_mean_c?.coefficient?.toFixed(3) ??
                  "0.000"}
              </div>
              <p className="caption">Correlation coefficient (r)</p>
              <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted border border-border inline-block px-2 py-1">
                {correlations?.temperature_mean_c?.significant
                  ? "Statistically significant"
                  : "Not statistically significant"}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-0 border-t border-border">
          <CardHeader>
            <CardTitle>Solar Radiation vs. Yield</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-center py-8">
              <div className="metric">
                {correlations?.solar_radiation_mj_m2?.coefficient?.toFixed(3) ??
                  "0.000"}
              </div>
              <p className="caption">Correlation coefficient (r)</p>
              <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted border border-border inline-block px-2 py-1">
                {correlations?.solar_radiation_mj_m2?.significant
                  ? "Statistically significant"
                  : "Not statistically significant"}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Summary Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="ruled-grid grid-cols-1 md:grid-cols-3">
              {corrRows.map((row) => (
                <div key={row.variable} className="p-4">
                  <p className="caption">{row.variable}</p>
                  <p className="metric text-lg mt-1">
                    r = {row.coefficient.toFixed(2)}
                  </p>
                  <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mt-1">
                    {row.significant
                      ? "Statistically significant"
                      : "Not significant"}{" "}
                    (p = {row.pValue.toFixed(3)}){" "}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
