"use client";

import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { getDistricts } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { useFilterStore } from "@/hooks/useFilters";

export function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const setSelectedDistrict = useFilterStore((s) => s.setSelectedDistrict);
  const [query, setQuery] = useState("");

  const { data: districtsData } = useQuery({
    queryKey: ["districts", query],
    queryFn: () => getDistricts(),
    staleTime: 300000,
    enabled: query.length >= 1,
  });
  const districts = (districtsData?.districts || [])
    .filter((d: { name: string }) => d.name.toLowerCase().includes(query.toLowerCase()))
    .slice(0, 10);

  const handleDistrictSelect = (districtId: number) => {
    setSelectedDistrict(districtId);
    navigate("/yields");
    setQuery("");
  };

  return (
    <header className="sticky top-0 z-30 bg-bg-primary border-b border-border">
      <div className="h-0.75 bg-accent w-full" aria-hidden />
      <div className="max-w-350 mx-auto h-16 flex items-center justify-between px-4 md:px-6 gap-4">
        <div className="flex items-center gap-2.5 shrink-0">
          <div className="block lg:hidden w-8 shrink-0" aria-hidden />
          <svg
            width="28"
            height="28"
            viewBox="0 0 32 32"
            role="img"
            aria-label="Nepal Ag Intelligence"
            className="shrink-0"
          >
            <rect width="32" height="32" fill="#050505" />
            <rect x="0" y="0" width="32" height="3" fill="#E61919" />
            <rect x="6" y="9" width="3" height="14" fill="#F4F4F0" />
            <rect x="14" y="9" width="3" height="11" fill="#F4F4F0" />
            <rect x="23" y="9" width="3" height="14" fill="#F4F4F0" />
            <rect x="6" y="22" width="20" height="3" fill="#E61919" />
          </svg>
          <h2 className="font-black text-sm uppercase tracking-tight leading-none">
            <span className="text-text-secondary font-medium font-mono text-xs tracking-widest">Nepal Ag</span>{" "}
            Intelligence
          </h2>
          <span className="hidden sm:inline font-mono text-[10px] uppercase tracking-widest text-text-muted border border-border-light px-1.5 py-0.5">REV 2.6</span>
        </div>

        <div className="hidden md:flex items-center flex-1 max-w-md mx-4 relative">
          <input
            type="search"
            placeholder="Search district…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && districts.length > 0) {
                handleDistrictSelect(districts[0].id);
              }
            }}
            className="w-full h-9 border border-border bg-bg-primary px-3 font-mono text-xs uppercase tracking-wider text-text-primary placeholder:text-text-muted placeholder:normal-case placeholder:tracking-normal focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
          />
          {query.length >= 1 && districts.length > 0 && (
            <ul className="absolute top-full left-0 z-50 mt-1 w-full bg-bg-primary border border-border">
              {districts.slice(0, 10).map((d: { id: number; name: string }) => (
                <li
                  key={d.id}
                  onClick={() => handleDistrictSelect(d.id)}
                  className="px-3 py-2 font-mono text-xs uppercase tracking-wider hover:bg-bg-tertiary cursor-pointer border-b border-border-light last:border-0"
                >
                  {d.name}
                </li>
              ))}
            </ul>
          )}
        </div>

        <nav className="flex items-center gap-1 shrink-0">
          <Link
            to="/about"
            className={cn(
              "px-3 py-2 font-mono text-xs uppercase tracking-widest transition-colors border border-transparent",
              location.pathname === "/about"
                ? "text-text-primary bg-bg-tertiary border-border"
                : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary",
            )}
          >
            About
          </Link>
          <a
            href="https://github.com/Aashish-po/nepal-ag-dashboard"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-2 font-mono text-xs uppercase tracking-widest text-text-secondary hover:text-text-primary hover:bg-bg-tertiary border border-transparent transition-colors"
          >
            GitHub
          </a>
          <span className="hidden lg:inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-text-muted border border-border-light px-2 py-1 ml-1">
            <span className="w-2 h-2 bg-accent inline-block" aria-hidden /> LIVE
          </span>
        </nav>
      </div>
    </header>
  );
}
