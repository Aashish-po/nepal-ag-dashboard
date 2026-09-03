import axios from 'axios'
import type {
  ClimateResponse,
  CommercializationRankingsResponse,
  CommercializationResponse,
  CorrelationResponse,
  CropListResponse,
  DistrictListResponse,
  ExportCropsResponse,
  ForecastResponse,
  HeatmapResponse,
  HealthResponse,
  YieldTimeseriesResponse,
} from './types'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getHealth(): Promise<HealthResponse> {
  const response = await apiClient.get('/health')
  return response.data
}

export async function getDistricts(params?: {
  province?: string
  region?: string
}): Promise<DistrictListResponse> {
  const filtered = Object.fromEntries(
    Object.entries(params ?? {}).filter(([, v]) => v !== undefined),
  )
  const response = await apiClient.get('/api/v1/districts', { params: filtered || undefined })
  return response.data
}

export async function getCrops(params?: {
  category?: string
}): Promise<CropListResponse> {
  const filtered = Object.fromEntries(
    Object.entries(params ?? {}).filter(([, v]) => v !== undefined),
  )
  const response = await apiClient.get('/api/v1/crops', { params: filtered || undefined })
  return response.data
}

export async function getYields(
  districtId: number,
  cropId: number,
  yearStart?: number,
  yearEnd?: number,
): Promise<YieldTimeseriesResponse> {
  const params: Record<string, unknown> = {}
  if (yearStart !== undefined) params.year_start = yearStart
  if (yearEnd !== undefined) params.year_end = yearEnd
  const response = await apiClient.get(`/api/v1/yields/${districtId}/${cropId}`, {
    params: Object.keys(params).length ? params : undefined,
  })
  return response.data
}

export async function getClimate(
  districtId: number,
  dateStart?: string,
  dateEnd?: string,
): Promise<ClimateResponse> {
  const params: Record<string, unknown> = {}
  if (dateStart !== undefined) params.date_start = dateStart
  if (dateEnd !== undefined) params.date_end = dateEnd
  const response = await apiClient.get(`/api/v1/climate/${districtId}`, {
    params: Object.keys(params).length ? params : undefined,
  })
  return response.data
}

export async function getCorrelation(
  districtId: number,
  cropId?: number,
  lagMonths?: number,
): Promise<CorrelationResponse> {
  const params: Record<string, unknown> = {}
  if (cropId !== undefined) params.crop_id = cropId
  if (lagMonths !== undefined) params.lag_months = lagMonths
  const response = await apiClient.get(`/api/v1/correlation/${districtId}`, {
    params: Object.keys(params).length ? params : undefined,
  })
  return response.data
}

export async function getExportCrops(
  districtId: number,
  year?: number,
): Promise<ExportCropsResponse> {
  const params: Record<string, unknown> = {}
  if (year !== undefined) params.year = year
  const response = await apiClient.get(`/api/v1/export-crops/${districtId}`, {
    params: Object.keys(params).length ? params : undefined,
  })
  return response.data
}

export async function getCommercialization(
  districtId: number,
  year?: number,
): Promise<CommercializationResponse> {
  const params: Record<string, unknown> = {}
  if (year !== undefined) params.year = year
  const response = await apiClient.get(`/api/v1/commercialization/${districtId}`, {
    params: Object.keys(params).length ? params : undefined,
  })
  return response.data
}

export async function getCommercializationList(
  year?: number,
  province?: string,
): Promise<CommercializationRankingsResponse> {
  const params: Record<string, unknown> = {}
  if (year !== undefined) params.year = year
  if (province !== undefined) params.province = province
  const response = await apiClient.get('/api/v1/commercialization', {
    params: Object.keys(params).length ? params : undefined,
  })
  return response.data
}

export async function getForecasts(
  districtId: number,
  cropId: number,
  monthsAhead: number = 12,
): Promise<ForecastResponse> {
  const response = await apiClient.get(`/api/v1/forecasts/${districtId}/${cropId}`, {
    params: { months_ahead: monthsAhead },
  })
  return response.data
}

export async function downloadYieldsCsv(
  params: Record<string, unknown>,
): Promise<Blob> {
  const response = await apiClient.get('/api/v1/export/yields', {
    params,
    responseType: 'blob',
  })
  return response.data
}

export async function downloadForecastsExcel(
  params: Record<string, unknown>,
): Promise<Blob> {
  const response = await apiClient.get('/api/v1/export/forecasts', {
    params,
    responseType: 'blob',
  })
  return response.data
}

export async function getHeatmap(): Promise<HeatmapResponse> {
  const response = await apiClient.get('/api/v1/heatmap/yield-climate-correlation')
  return response.data
}