import { useQuery } from "@tanstack/react-query";
import { getForecasts, downloadForecastsExcel } from "@/lib/api";
import { useFilterStore } from "@/hooks/useFilters";
import { formatNumber } from "@/lib/utils";
import { FilterBar } from "@/components/FilterBar";
import { TableSkeleton } from "@/components/Loading";
import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
} from "recharts";

export function Forecasts() {
  const { selectedDistrict, selectedCrop, monthsAhead, setMonthsAhead } =
    useFilterStore();
  const [exportLoading, setExportLoading] = useState(false);

  const {
    data: forecastData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["forecasts", selectedDistrict, selectedCrop, monthsAhead],
    queryFn: () => getForecasts(selectedDistrict!, selectedCrop!, monthsAhead),
    enabled: !!selectedDistrict && !!selectedCrop,
    staleTime: 300000,
  });

  if (!selectedDistrict || !selectedCrop) {
    return (
      <div className="max-w-[1400px] mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12">
          <p className="text-text-secondary">
            Select a district and crop to view forecasts.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-[1400px] mx-auto p-6">
        <FilterBar showCropSelector />
        <TableSkeleton rows={5} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-[1400px] mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12">
          <p className="text-text-secondary">Could not load forecast data.</p>
        </div>
      </div>
    );
  }

  if (!forecastData) {
    return (
      <div className="max-w-[1400px] mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12">
          <p className="text-text-secondary">No forecast data available.</p>
        </div>
      </div>
    );
  }

  const { forecasts, model_diagnostics, forecast_model, recommendation } =
    forecastData;

  const chartData = (forecasts ?? []).map((f: any) => ({
    month: f.forecast_month,
    forecast: f.forecast_yield_kg_ha,
    lower: f.lower_ci_95,
    upper: f.upper_ci_95,
  }));

  const diagnostics = {
    model: forecast_model,
    rmse:
      model_diagnostics?.rmse_kg_ha != null
        ? `${formatNumber(model_diagnostics.rmse_kg_ha)} kg/ha`
        : "-",
    recommendation: recommendation || "No recommendation available",
  };

  const handleExport = async () => {
    setExportLoading(true);
    try {
      const blob = await downloadForecastsExcel({
        district_id: selectedDistrict,
        crop_id: selectedCrop,
        months_ahead: monthsAhead,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `forecast_${selectedDistrict}_${selectedCrop}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
      alert("Failed to download Excel. Please try again.");
    } finally {
      setExportLoading(false);
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Forecasts</h1>
        <button
          className={`px-4 py-2 border border-border rounded-md text-sm hover:bg-bg-tertiary ${
            exportLoading ? "opacity-50 cursor-not-allowed" : ""
          }`}
          onClick={handleExport}
          disabled={exportLoading}
        >
          {exportLoading ? "Exporting..." : "Download Excel"}
        </button>
      </div>

      <FilterBar showCropSelector />
      <div className="flex gap-2 mb-6">
        {[12, 24, 36].map((months) => (
          <button
            key={months}
            className={`px-4 py-2 rounded-md text-sm ${
              monthsAhead === months
                ? "bg-primary text-white"
                : "border border-hover:bg-bg-tertiary"
            }`}
            onClick={() => setMonthsAhead(months)}
          >
            {months} months
          </button>
        ))}
      </div>
      {chartData.length > 0 && (
        <div className="bg-white border border-border rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold mb-4">
            Yield Forecast with 95% Confidence Interval
          </h3>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis
                domain={["dataMin", "dataMax"]}
                tickFormatter={(v) => (v !== null ? `${formatNumber(v)}` : "-")}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-bg-primary)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "var(--radius-md)",
                }}
              />
              <Legend verticalAlign="top" height={36} />
              {/* Confidence interval area - created by subtracting two areas */}
              <Area
                type="monotone"
                dataKey="upper"
                fill="#8884d8"
                fillOpacity={0.2}
              />
              <Area
                type="monotone"
                dataKey="lower"
                fill="var(--color-bg-primary)"
                fillOpacity={1}
              />
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="var(--color-primary)"
                name="Forecast"
              />
              <Line
                type="monotone"
                dataKey="lower"
                stroke="var(--color-secondary)"
                strokeDasharray="5 5"
                name="Lower CI"
              />
              <Line
                type="monotone"
                dataKey="upper"
                stroke="var(--color-secondary)"
                strokeDasharray="5 5"
                name="Upper CI"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white border border-border rounded-lg p-4">
          <p className="text-sm text-text-secondary">Model</p>
          <p className="text-lg font-bold mt-1">{diagnostics.model}</p>
        </div>
        <div className="bg-white border border-border rounded-lg p-4">
          <p className="text-sm text-text-secondary">Historical RMSE</p>
          <p className="text-lg font-bold mt-1">{diagnostics.rmse}</p>
        </div>
        <div className="bg-white border border-border rounded-lg p-4">
          <p className="text-sm text-text-secondary">Recommendation</p>
          <p className="text-lg font-bold mt-1 text-primary">
            {diagnostics.recommendation}
          </p>
        </div>
      </div>

      <div className="bg-white border border-border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Forecast Table</h3>
        <div className="overflow-x-auto">
          <table className="w-full whitespace-nowrap">
            <thead>
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary">
                  Month
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary">
                  Forecast (kg/ha)
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary">
                  Lower 95% CI
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-text-secondary">
                  Upper 95% CI
                </th>
              </tr>
            </thead>
            <tbody>
              {(forecasts ?? []).map((f: any, index: number) => (
                <tr key={index} className="border-b">
                  <td className="px-4 py-2">{f.forecast_month}</td>
                  <td className="px-4 py-2">
                    {f.forecast_yield_kg_ha != null
                      ? `${formatNumber(f.forecast_yield_kg_ha)}`
                      : "-"}
                  </td>
                  <td className="px-4 py-2">
                    {f.lower_ci_95 != null
                      ? `${formatNumber(f.lower_ci_95)}`
                      : "-"}
                  </td>
                  <td className="px-4 py-2">
                    {f.upper_ci_95 != null
                      ? `${formatNumber(f.upper_ci_95)}`
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
