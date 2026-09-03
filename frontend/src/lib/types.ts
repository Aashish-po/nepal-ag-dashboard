// ponytail: mirrors backend/api/models/schemas.py — keeps frontend typed without
// importing the server's Pydantic models; the shapes are kept in sync by hand.

export interface District {
  id: number;
  name: string;
  province: string;
  region: string | null;
  latitude: number | null;
  longitude: number | null;
  population: number | null;
  area_sq_km: number | null;
}

export interface DistrictListResponse {
  total: number;
  districts: District[];
}

export interface Crop {
  id: number;
  name: string;
  fao_code: string | null;
  category: string | null;
  unit: string;
  is_export_crop: boolean | null;
  is_subsistence: boolean | null;
}

export interface CropListResponse {
  total: number;
  crops: Crop[];
}

export interface YieldRecord {
  id: number | null;
  district_id: number | null;
  crop_id: number | null;
  year: number;
  production_mt: number | null;
  area_harvested_ha: number | null;
  yield_kg_ha: number | null;
  data_source: string | null;
  data_quality: string;
}

export interface YieldStatistics {
  avg_yield_kg_ha: number | null;
  max_yield_kg_ha: number | null;
  min_yield_kg_ha: number | null;
  volatility: number | null;
  cagr_pct: number | null;
  trend: string | null;
}

export interface YieldTimeseriesResponse {
  district_id: number;
  district_name: string;
  crop_id: number;
  crop_name: string;
  timeseries: YieldRecord[];
  statistics: YieldStatistics;
}

export interface ClimateRecord {
  id: number | null;
  district_id: number | null;
  observation_date: string;
  rainfall_mm: number | null;
  temperature_min_c: number | null;
  temperature_max_c: number | null;
  temperature_mean_c: number | null;
  solar_radiation_mj_m2: number | null;
  data_source: string | null;
}

export interface ClimateSummary {
  annual_rainfall_mm: number | null;
  avg_temperature_c: number | null;
  monsoon_start_month: number | null;
  monsoon_end_month: number | null;
}

export interface ClimateResponse {
  district_id: number;
  district_name: string;
  data: ClimateRecord[];
  summary: ClimateSummary;
}

export interface CorrelationComponent {
  coefficient: number | null;
  p_value: number | null;
  significant: boolean;
}

export interface CorrelationResponse {
  district_id: number;
  district_name: string;
  crop_id: number;
  crop_name: string;
  lag_months: number;
  correlations: Record<string, CorrelationComponent>;
  r_squared: number | null;
  interpretation: string | null;
}

export interface ExportSeason {
  start_month: number;
  end_month: number;
}

export interface ExportCropInfo {
  crop_id: number;
  crop_name: string;
  production_mt: number | null;
  area_harvested_ha: number | null;
  yield_kg_ha: number | null;
  export_potential_mt: number | null;
  avg_price_usd_per_mt: number | null;
  estimated_revenue_usd: number | null;
  export_season: ExportSeason | null;
  main_export_countries: string[];
}

export interface ExportCropsResponse {
  district_id: number;
  district_name: string;
  year: number;
  export_crops: ExportCropInfo[];
  total_export_revenue_usd: number | null;
}

export interface CommercializationComponents {
  export_crop_contribution: number | null;
  farm_size_contribution: number | null;
  export_volume_contribution: number | null;
}

export interface CommercializationResponse {
  district_id: number;
  district_name: string;
  year: number;
  export_crop_area_pct: number | null;
  subsistence_area_pct: number | null;
  other_area_pct: number | null;
  avg_holding_size_ha: number | null;
  export_volume_ratio: number | null;
  commercialization_score: number | null;
  commercialization_level: string | null;
  components: CommercializationComponents | null;
}

export interface CommercializationRankResponse {
  rank: number;
  district_name: string;
  district_id: number;
  commercialization_score: number;
  export_crop_area_pct: number | null;
  subsistence_area_pct: number | null;
  commercialization_level: string | null;
  province: string | null;
}

export interface CommercializationRankingsResponse {
  year: number;
  total: number;
  districts: CommercializationRankResponse[];
}

export interface ForecastMonth {
  forecast_month: string;
  forecast_yield_kg_ha: number | null;
  lower_ci_95: number | null;
  upper_ci_95: number | null;
  confidence: number | null;
  forecast_model: string | null;
  forecast_date: string | null;
}

export interface HeatmapRow {
  district: string;
  district_id: number;
  crop: string;
  crop_id: number;
  rainfall_corr: number | null;
  temperature_corr: number | null;
  solar_corr: number | null;
}

export interface HeatmapResponse {
  total_rows: number;
  rows: HeatmapRow[];
}

export interface ModelDiagnostics {
  rmse_kg_ha: number | null;
  mae_kg_ha: number | null;
  mape_pct: number | null;
}

export interface ForecastResponse {
  district_id: number;
  district_name: string;
  crop_id: number;
  crop_name: string;
  forecast_horizon_months: number;
  forecast_model: string | null;
  model_diagnostics: ModelDiagnostics;
  forecasts: ForecastMonth[];
  recommendation: string | null;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  database: string;
}
