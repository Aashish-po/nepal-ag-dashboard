import { create } from 'zustand'

export interface FilterState {
  selectedDistrict: number | null
  selectedCrop: number | null
  yearStart: number | null
  yearEnd: number | null
  monthsAhead: number
  setSelectedDistrict: (id: number | null) => void
  setSelectedCrop: (id: number | null) => void
  setYearStart: (year: number | null) => void
  setYearEnd: (year: number | null) => void
  setMonthsAhead: (months: number) => void
  reset: () => void
}

const initialState = {
  selectedDistrict: null as number | null,
  selectedCrop: null as number | null,
  yearStart: null as number | null,
  yearEnd: null as number | null,
  monthsAhead: 12,
}

export const useFilterStore = create<FilterState>((set) => ({
  ...initialState,
  setSelectedDistrict: (selectedDistrict) => set({ selectedDistrict }),
  setSelectedCrop: (selectedCrop) => set({ selectedCrop }),
  setYearStart: (yearStart) => set({ yearStart }),
  setYearEnd: (yearEnd) => set({ yearEnd }),
  setMonthsAhead: (monthsAhead) => set({ monthsAhead }),
  reset: () => set(initialState),
}))
