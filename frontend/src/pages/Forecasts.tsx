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
    refetch,
  } = useQuery({
    queryKey: ["forecasts", selectedDistrict, selectedCrop, monthsAhead],
    queryFn: () => getForecasts(selectedDistrict!, selectedCrop!, monthsAhead),
    enabled: !!selectedDistrict && !!selectedCrop,
    staleTime: 300000,
  });

  if (!selectedDistrict || !selectedCrop) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            Select a district and crop to view forecasts.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector />
        <TableSkeleton rows={5} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {"// Could not load forecast data. — "}
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

  if (!forecastData) {
    return (
      <div className="max-w-350 mx-auto p-6">
        <FilterBar showCropSelector />
        <div className="text-center py-12 border border-border">
          <p className="font-mono text-xs uppercase tracking-widest text-text-secondary">No forecast data available.</p>
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
    <div className="max-w-350 mx-auto p-6">
      <div className="flex items-center justify-between mb-6 border-b border-border pb-3">
        <h1 className="font-black uppercase tracking-tight text-h1">Forecasts</h1>
        <button
          className={`px-4 py-2 border border-border font-mono text-xs uppercase tracking-widest hover:bg-bg-secondary ${
            exportLoading ? "opacity-50 cursor-not-allowed" : ""
          }`}
          onClick={handleExport}
          disabled={exportLoading}
        >
          {exportLoading ? "Exporting..." : "Download Excel"}
        </button>
      </div>

      <FilterBar showCropSelector />
      <div className="flex gap-0 mb-6 border border-border w-fit">
        {[12, 24, 36].map((months) => (
          <button
            key={months}
            className={`px-4 py-2 font-mono text-xs uppercase tracking-widest border-r last:border-r-0 border-border ${
              monthsAhead === months
                ? "bg-text-primary text-bg-primary"
                : "hover:bg-bg-secondary"
            }`}
            onClick={() => setMonthsAhead(months)}
          >
            {months} mo
          </button>
        ))}
      </div>
      {chartData.length > 0 && (
        <div className="border border-border p-4 mb-6">
          <h3 className="font-mono text-xs uppercase tracking-widest mb-4">
            Yield Forecast with 95% Confidence Interval
          </h3>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="var(--color-grid)" strokeDasharray="0" vertical={false} />
              <XAxis dataKey="month" stroke="var(--color-axis)" fontSize={11} fontFamily="var(--font-family-mono)" tickLine={false} />
              <YAxis
                domain={["dataMin", "dataMax"]}
                stroke="var(--color-axis)" fontSize={11} fontFamily="var(--font-family-mono)" tickLine={false} axisLine={false}
                tickFormatter={(v) => (v !== null ? `${formatNumber(v)}` : "-")}
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
                cursor={{ stroke: 'var(--color-accent)', strokeWidth: 1, strokeDasharray: '4 4' }}
              />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontFamily: 'var(--font-family-mono)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '.06em' }} />
              <Area
                type="monotone"
                dataKey="upper"
                fill="var(--color-ci-band)"
                stroke="none"
                fillOpacity={1}
              />
              <Area
                type="monotone"
                dataKey="lower"
                fill="var(--color-bg-primary)"
                stroke="none"
                fillOpacity={1}
              />
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="var(--color-text-primary)"
                strokeWidth={2}
                dot={false}
                name="Forecast"
              />
              <Line
                type="monotone"
                dataKey="lower"
                stroke="var(--color-accent)"
                strokeDasharray="5 5"
                strokeWidth={1}
                dot={false}
                name="Lower CI"
              />
              <Line
                type="monotone"
                dataKey="upper"
                stroke="var(--color-accent)"
                strokeDasharray="5 5"
                strokeWidth={1}
                dot={false}
                name="Upper CI"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="ruled-grid grid-cols-1 md:grid-cols-3 mb-6">
        <div className="p-4 text-center">
          <p className="caption">Model</p>
          <p className="font-mono text-sm font-bold uppercase tracking-wider mt-1">{diagnostics.model}</p>
        </div>
        <div className="p-4 text-center">
          <p className="caption">Historical RMSE</p>
          <p className="font-mono text-sm font-bold uppercase tracking-wider mt-1">{diagnostics.rmse}</p>
        </div>
        <div className="p-4 text-center">
          <p className="caption">Recommendation</p>
          <p className="font-mono text-xs font-medium uppercase tracking-wider mt-1 leading-relaxed">
            {diagnostics.recommendation}
          </p>
        </div>
      </div>

      <div className="border border-border p-4">
        <h3 className="font-mono text-xs uppercase tracking-widest mb-4">Forecast Table</h3>
        <div className="overflow-x-auto">
          <table className="w-full whitespace-nowrap">
            <thead>
              <tr className="border-b-2 border-border">
                <th className="px-4 py-2 text-left font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Month
                </th>
                <th className="px-4 py-2 text-right font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Forecast (kg/ha)
                </th>
                <th className="px-4 py-2 text-right font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Lower 95% CI
                </th>
                <th className="px-4 py-2 text-right font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Upper 95% CI
                </th>
              </tr>
            </thead>
            <tbody>
              {(forecasts ?? []).map((f: any, index: number) => (
                <tr key={index} className="border-b border-border-light hover:bg-bg-secondary">
                  <td className="px-4 py-2 font-mono text-xs">{f.forecast_month}</td>
                  <td className="px-4 py-2 font-mono text-xs text-right tabular-nums">
                    {f.forecast_yield_kg_ha != null
                      ? `${formatNumber(f.forecast_yield_kg_ha)}`
                      : "-"}
                  </td>
                  <td className="px-4 py-2 font-mono text-xs text-right tabular-nums">
                    {f.lower_ci_95 != null
                      ? `${formatNumber(f.lower_ci_95)}`
                      : "-"}
                  </td>
                  <td className="px-4 py-2 font-mono text-xs text-right tabular-nums">
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
