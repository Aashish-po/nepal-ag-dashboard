import { useQuery } from "@tanstack/react-query";
import { Button } from "@/shadcn/button";
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
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Could not load correlation data.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading || !correlationData) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12">
          <p className="text-text-secondary">
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
        <div className="text-center py-12">
          <p className="text-text-secondary">
            No correlation results for this district and crop.
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
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Yield-Climate Correlation</h1>
        <Button
          variant="outline"
          onClick={() => alert("Export analysis triggered")}
        >
          Download Matrix
        </Button>
      </div>

      <FilterBar showCropSelector />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Correlation Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {corrRows.map((row) => (
                <div key={row.variable} className="flex items-center gap-4">
                  <div className="w-40 text-sm font-medium">{row.variable}</div>
                  <div
                    className="flex-1 h-8 rounded-md relative overflow-hidden"
                    style={{
                      backgroundColor:
                        row.coefficient > 0
                          ? "rgba(46, 125, 50, 0.15)"
                          : "rgba(229, 57, 53, 0.15)",
                    }}
                  >
                    <div
                      className="absolute inset-y-0 left-0 rounded-md"
                      style={{
                        width: `${Math.abs(row.coefficient) * 100}%`,
                        backgroundColor:
                          row.coefficient > 0
                            ? "var(--color-primary)"
                            : "var(--color-error)",
                      }}
                    />
                    <span className="absolute inset-0 flex items-center justify-center text-sm font-medium">
                      r = {row.coefficient.toFixed(2)}
                    </span>
                  </div>
                  <div className="w-24 text-right text-sm text-text-secondary">
                    p = {row.pValue.toFixed(3)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Rainfall vs. Yield</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-center py-8">
              <div className="text-2xl font-bold">
                {correlations?.rainfall_mm?.coefficient?.toFixed(3) ?? "0.000"}
              </div>
              <p className="text-sm text-text-secondary">
                Correlation coefficient (r)
              </p>
              <p className="text-xs text-text-muted">
                {correlations?.rainfall_mm?.significant
                  ? "Statistically significant"
                  : "Not statistically significant"}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Temperature vs. Yield</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-center py-8">
              <div className="text-2xl font-bold">
                {correlations?.temperature_mean_c?.coefficient?.toFixed(3) ??
                  "0.000"}
              </div>
              <p className="text-sm text-text-secondary">
                Correlation coefficient (r)
              </p>
              <p className="text-xs text-text-muted">
                {correlations?.temperature_mean_c?.significant
                  ? "Statistically significant"
                  : "Not statistically significant"}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Solar Radiation vs. Yield</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-center py-8">
              <div className="text-2xl font-bold">
                {correlations?.solar_radiation_mj_m2?.coefficient?.toFixed(3) ??
                  "0.000"}
              </div>
              <p className="text-sm text-text-secondary">
                Correlation coefficient (r)
              </p>
              <p className="text-xs text-text-muted">
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
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {corrRows.map((row) => (
                <div
                  key={row.variable}
                  className="p-4 bg-bg-secondary rounded-lg"
                >
                  <p className="text-sm text-text-secondary">{row.variable}</p>
                  <p className="text-xl font-bold mt-1">
                    r = {row.coefficient.toFixed(2)}
                  </p>
                  <p className="text-sm text-text-muted mt-1">
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
