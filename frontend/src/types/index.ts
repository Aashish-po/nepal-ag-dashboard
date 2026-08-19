export interface District {
  id: number
  name: string
  province: string
  latitude?: number
  longitude?: number
  area_ha?: number
  population?: number
}

export interface Crop {
  id: number
  name: string
  category: string
  scientific_name?: string
  season: 'kharif' | 'rabi' | 'annual'
  is_export_crop: boolean
}

export interface YieldRecord {
  district_id: number
  crop_id: number
  year: number
  production_mt: number
  area_harvested_ha: number
  yield_kg_ha: number
  data_quality: 'HIGH' | 'MEDIUM' | 'LOW' | 'ESTIMATED'
  source: string
  trend?: 'INCREASING' | 'STABLE' | 'DECREASING'
  cagr?: number
}

export interface ClimateRecord {
  district_id: number
  date: string
  rainfall_mm: number
  temperature_mean_c: number
  temperature_min_c?: number
  temperature_max_c?: number
  solar_radiation_mj_m2: number
  data_quality: 'HIGH' | 'MEDIUM' | 'LOW' | 'INTERPOLATED'
}

export interface CorrelationResult {
  district_id: number
  crop_id: number
  variable: 'rainfall' | 'temperature' | 'solar_radiation'
  coefficient: number
  p_value: number
  r_squared: number
  lag_months?: number
  sample_size: number
  significant: boolean
}

export interface ExportCropRecord {
  district_id: number
  year: number
  crop_id: number
  production_mt: number
  export_volume_mt?: number
  avg_price_usd_mt?: number
  export_revenue_usd?: number
  export_markets: string[]
}

export interface CommercializationRecord {
  district_id: number
  year: number
  score: number
  export_area_pct: number
  subsistence_area_pct: number
  avg_holding_size_ha: number
  total_cultivated_ha: number
  export_crops_count: number
}

export interface ForecastRecord {
  district_id: number
  crop_id: number
  month: string
  forecast_yield: number
  lower_ci_95: number
  upper_ci_95: number
  model_name: string
  rmse: number
  months_ahead: number
}

export interface DistrictSummary {
  district_id: number
  district_name: string
  province: string
  avg_yield?: number
  top_crop?: string
  commercialization_score?: number
  trend?: string
}

export interface ApiResponse<T> {
  data: T
  meta?: {
    total: number
    page: number
    limit: number
  }
}

export interface FilterState {
  districts: number[]
  crops: number[]
  yearStart: number | null
  yearEnd: number | null
  province: string
  category: string
  metric: string
  monthsAhead: number
}

export interface StatsCard {
  label: string
  value: string | number
  unit?: string
  trend?: 'up' | 'down' | 'stable'
  change?: number
}
