"use client";

import { useQuery } from "@tanstack/react-query";
import { getDistricts, getCrops } from "@/lib/api";
import { useFilterStore } from "@/hooks/useFilters";

interface FilterBarProps {
  showCropSelector?: boolean;
  showYearRange?: boolean;
}

const YEARS = Array.from({ length: 11 }, (_, i) => 2014 + i);

export function FilterBar({
  showCropSelector = true,
  showYearRange = false,
}: FilterBarProps) {
  const {
    selectedDistrict,
    selectedCrop,
    yearStart,
    yearEnd,
    setSelectedDistrict,
    setSelectedCrop,
    setYearStart,
    setYearEnd,
  } = useFilterStore();

  const { data: districtsData } = useQuery({
    queryKey: ["districts"],
    queryFn: () => getDistricts(),
    staleTime: 3600000,
  });

  const { data: cropsData } = useQuery({
    queryKey: ["crops"],
    queryFn: () => getCrops(),
    staleTime: 3600000,
  });

const districts = districtsData?.districts || [];
  const crops = cropsData?.crops || [];

  return (
    <div className="flex flex-wrap gap-4 items-end mb-6">
      <div className="flex flex-col">
        <label className="text-xs text-text-secondary mb-1">District</label>
        <select
          className="w-50 h-10 px-3 rounded-md border border-border bg-bg-primary text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
          value={selectedDistrict?.toString() || ""}
          onChange={(e) =>
            setSelectedDistrict(
              e.target.value ? parseInt(e.target.value) : null,
            )
          }
        >
          <option value="">Select District</option>
          {districts.map((d: { id: number; name: string }) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
      </div>

      {showCropSelector && (
        <div className="flex flex-col">
          <label className="text-xs text-text-secondary mb-1">Crop</label>
          <select
            className="w-50 h-10 px-3 rounded-md border border-border bg-bg-primary text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
            value={selectedCrop?.toString() || ""}
            onChange={(e) =>
              setSelectedCrop(e.target.value ? parseInt(e.target.value) : null)
            }
          >
            <option value="">Select Crop</option>
            {crops.map((c: { id: number; name: string }) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {showYearRange && (
        <>
          <div className="flex flex-col">
            <label className="text-xs text-text-secondary mb-1">
              Year Start
            </label>
            <select
              className="w-30 h-10 px-3 rounded-md border border-border bg-bg-primary text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
              value={yearStart?.toString() || ""}
              onChange={(e) =>
                setYearStart(e.target.value ? parseInt(e.target.value) : null)
              }
            >
              <option value="">Any</option>
              {YEARS.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col">
            <label className="text-xs text-text-secondary mb-1">Year End</label>
            <select
              className="w-30 h-10 px-3 rounded-md border border-border bg-bg-primary text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
              value={yearEnd?.toString() || ""}
              onChange={(e) =>
                setYearEnd(e.target.value ? parseInt(e.target.value) : null)
              }
            >
              <option value="">Any</option>
              {YEARS.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>
        </>
      )}

    </div>
  );
}
