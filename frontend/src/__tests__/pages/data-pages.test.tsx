import { describe, it, expect, beforeEach, vi } from "vitest";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../test-utils";
import * as api from "@/lib/api";
import { useFilterStore } from "@/hooks/useFilters";
import { Yields } from "@/pages/Yields";
import { Climate } from "@/pages/Climate";
import { Correlation } from "@/pages/Correlation";
import { ExportCrops } from "@/pages/ExportCrops";
import { Commercialization } from "@/pages/Commercialization";
import { Forecasts } from "@/pages/Forecasts";
import { Compare } from "@/pages/Compare";

vi.mock("@/lib/api");

beforeEach(() => {
  useFilterStore.getState().reset();
  // FilterBar loads these on every page; the always-on commercialization
  // list query must resolve a defined value (react-query rejects undefined).
  vi.mocked(api.getDistricts).mockResolvedValue({ districts: [] });
  vi.mocked(api.getCrops).mockResolvedValue({ crops: [] });
  vi.mocked(api.getCommercializationList).mockResolvedValue({ districts: [] });
});

describe("data pages — default empty states", () => {
  it("Yields prompts for district + crop", async () => {
    renderWithProviders(<Yields />);
    expect(
      await screen.findByText(
        /select a district and crop to view yield trends/i,
      ),
    ).toBeInTheDocument();
  });

  it("Climate prompts for a district", async () => {
    renderWithProviders(<Climate />);
    expect(
      await screen.findByText(/select a district to view climate data/i),
    ).toBeInTheDocument();
  });

  it("Correlation prompts for district + crop", async () => {
    renderWithProviders(<Correlation />);
    expect(
      await screen.findByText(
        /select a district and crop to view correlation analysis/i,
      ),
    ).toBeInTheDocument();
  });

  it("ExportCrops prompts for a district", async () => {
    renderWithProviders(<ExportCrops />);
    expect(
      await screen.findByText(/select a district to view export crop data/i),
    ).toBeInTheDocument();
  });

  it("Forecasts prompts for district + crop", async () => {
    renderWithProviders(<Forecasts />);
    expect(
      await screen.findByText(/select a district and crop to view forecasts/i),
    ).toBeInTheDocument();
  });

  it("Compare prompts to pick districts", async () => {
    renderWithProviders(<Compare />);
    expect(
      await screen.findByText(/select districts to compare/i),
    ).toBeInTheDocument();
  });

  it("Commercialization renders the dashboard once rankings load", async () => {
    renderWithProviders(<Commercialization />);
    expect(
      await screen.findByText("Commercialization Dashboard"),
    ).toBeInTheDocument();
  });
});

describe("Yields — data + export journey", () => {
  beforeEach(() => {
    useFilterStore.setState({ selectedDistrict: 1, selectedCrop: 1 });
    vi.mocked(api.getYields).mockResolvedValue({
      district_name: "Kathmandu",
      crop_name: "Rice",
      timeseries: [{ year: 2020, yield_kg_ha: 3000, production_mt: 100 }],
      statistics: {
        avg_yield_kg_ha: 3000,
        max_yield_kg_ha: 3200,
        min_yield_kg_ha: 2800,
        volatility: 100,
      },
    });
  });

  it("renders stats and chart title from loaded data", async () => {
    renderWithProviders(<Yields />);
    expect(
      await screen.findByText("Rice — Kathmandu Yield Trends"),
    ).toBeInTheDocument();
    expect(screen.getByText("Average Yield")).toBeInTheDocument();
    expect(screen.getByText("3,000 kg/ha")).toBeInTheDocument();
  });

  it("Export CSV calls the download API with current filters", async () => {
    window.URL.createObjectURL = vi.fn(() => "blob:x");
    window.URL.revokeObjectURL = vi.fn();
    vi.mocked(api.downloadYieldsCsv).mockResolvedValue(
      new Blob(["year\n2020"]),
    );

    renderWithProviders(<Yields />);
    await screen.findByText("Rice — Kathmandu Yield Trends");
    fireEvent.click(screen.getByRole("button", { name: /export csv/i }));

    await waitFor(() =>
      expect(api.downloadYieldsCsv).toHaveBeenCalledWith({
        district_id: 1,
        crop_id: 1,
        year_start: null,
        year_end: null,
      }),
    );
  });
});

describe("Forecasts — data + export journey", () => {
  beforeEach(() => {
    useFilterStore.setState({ selectedDistrict: 1, selectedCrop: 1 });
    vi.mocked(api.getForecasts).mockResolvedValue({
      forecast_model: "ARIMA",
      recommendation: "Stable outlook",
      model_diagnostics: { rmse_kg_ha: 120 },
      forecasts: [
        {
          forecast_month: "2025-01",
          forecast_yield_kg_ha: 3000,
          lower_ci_95: 2800,
          upper_ci_95: 3200,
        },
      ],
    });
  });

  it("renders diagnostics and forecast table from loaded data", async () => {
    renderWithProviders(<Forecasts />);
    expect(await screen.findByText("ARIMA")).toBeInTheDocument();
    expect(screen.getByText("Stable outlook")).toBeInTheDocument();
    expect(screen.getByText("2025-01")).toBeInTheDocument();
  });

  it("Download Excel calls the export API with months_ahead", async () => {
    window.URL.createObjectURL = vi.fn(() => "blob:x");
    window.URL.revokeObjectURL = vi.fn();
    vi.mocked(api.downloadForecastsExcel).mockResolvedValue(new Blob(["x"]));

    renderWithProviders(<Forecasts />);
    await screen.findByText("ARIMA");
    fireEvent.click(screen.getByRole("button", { name: /download excel/i }));

    await waitFor(() =>
      expect(api.downloadForecastsExcel).toHaveBeenCalledWith({
        district_id: 1,
        crop_id: 1,
        months_ahead: 12,
      }),
    );
  });
});

describe("Correlation — loaded analysis", () => {
  beforeEach(() => {
    useFilterStore.setState({ selectedDistrict: 1, selectedCrop: 2 });
    vi.mocked(api.getCorrelation).mockResolvedValue({
      correlations: {
        rainfall_mm: { coefficient: 0.52, p_value: 0.01, significant: true },
        temperature_mean_c: { coefficient: -0.3, p_value: 0.2, significant: false },
      },
    });
  });

  it("renders the heatmap and summary sections", async () => {
    renderWithProviders(<Correlation />);
    expect(await screen.findByText("Correlation Heatmap")).toBeInTheDocument();
    expect(screen.getByText("Summary Statistics")).toBeInTheDocument();
  });
});
