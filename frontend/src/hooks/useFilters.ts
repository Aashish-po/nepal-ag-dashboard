import { create } from 'zustand'

export interface FilterState {
  districts: number[]
  crops: number[]
  yearStart: number | null
  yearEnd: number | null
  province: string
  category: string
  metric: string
  monthsAhead: number
  compareDistricts: number[]
  setDistricts: (ids: number[]) => void
  setCrops: (ids: number[]) => void
  setYearStart: (year: number | null) => void
  setYearEnd: (year: number | null) => void
  setProvince: (province: string) => void
  setCategory: (category: string) => void
  setMetric: (metric: string) => void
  setMonthsAhead: (months: number) => void
  setCompareDistricts: (ids: number[]) => void
  reset: () => void
}

const initialState = {
  districts: [] as number[],
  crops: [] as number[],
  yearStart: null as number | null,
  yearEnd: null as number | null,
  province: '',
  category: '',
  metric: 'avg_yield',
  monthsAhead: 12,
  compareDistricts: [] as number[],
}

export const useFilterStore = create<FilterState>((set) => ({
  ...initialState,
  setDistricts: (districts) => set({ districts }),
  setCrops: (crops) => set({ crops }),
  setYearStart: (yearStart) => set({ yearStart }),
  setYearEnd: (yearEnd) => set({ yearEnd }),
  setProvince: (province) => set({ province }),
  setCategory: (category) => set({ category }),
  setMetric: (metric) => set({ metric }),
  setMonthsAhead: (monthsAhead) => set({ monthsAhead }),
  setCompareDistricts: (compareDistricts) => set({ compareDistricts }),
  reset: () => set(initialState),
}))
