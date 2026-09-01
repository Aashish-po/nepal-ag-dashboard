import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getDistricts(params?: { province?: string }) {
  const response = await apiClient.get('/api/v1/districts', { params })
  return response.data
}

export async function getCrops(params?: { category?: string }) {
  const response = await apiClient.get('/api/v1/crops', { params })
  return response.data
}

export async function getYields(districtId: number, cropId: number, yearStart?: number, yearEnd?: number) {
  const response = await apiClient.get(`/api/v1/yields/${districtId}/${cropId}`, {
    params: { year_start: yearStart, year_end: yearEnd },
  })
  return response.data
}

export async function getClimate(districtId: number, dateStart?: string, dateEnd?: string) {
  const response = await apiClient.get(`/api/v1/climate/${districtId}`, {
    params: { date_start: dateStart, date_end: dateEnd },
  })
  return response.data
}

export async function getCorrelation(districtId: number, cropId: number) {
  const response = await apiClient.get(`/api/v1/correlation/${districtId}`, {
    params: { crop_id: cropId },
  })
  return response.data
}

export async function getExportCrops(districtId: number) {
  const response = await apiClient.get(`/api/v1/export-crops/${districtId}`)
  return response.data
}

export async function getCommercialization(districtId: number, year?: number) {
  const response = await apiClient.get(`/api/v1/commercialization/${districtId}`, {
    params: { year },
  })
  return response.data
}

export async function getCommercializationList(year?: number, province?: string) {
  const response = await apiClient.get('/api/v1/commercialization', { params: { year, province } })
  return response.data
}

export async function getForecasts(districtId: number, cropId: number, monthsAhead: number = 12) {
  const response = await apiClient.get(`/api/v1/forecasts/${districtId}/${cropId}`, {
    params: { months_ahead: monthsAhead },
  })
  return response.data
}

export async function downloadYieldsCsv(params: Record<string, unknown>) {
  const response = await apiClient.get('/api/v1/export/yields', {
    params,
    responseType: 'blob',
  })
  return response.data
}

export async function downloadForecastsExcel(params: Record<string, unknown>) {
  const response = await apiClient.get('/api/v1/export/forecasts', {
    params,
    responseType: 'blob',
  })
  return response.data
}
