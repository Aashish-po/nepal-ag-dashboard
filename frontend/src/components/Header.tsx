"use client";

import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { getDistricts } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export function Header() {
  const location = useLocation();
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

  return (
    <header className="sticky top-0 z-30 h-15 bg-bg-primary border-b border-border-primary">
      <div className="max-w-350 mx-auto h-full flex items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-3">
          <div className="md:hidden w-8" />
          <h2 className="text-lg font-semibold">
            <span className="text-text-secondary font-normal">Nepal Ag</span>{" "}
            Intelligence
          </h2>
        </div>

        <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
          <input
            type="search"
            placeholder="Search district…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full h-9 rounded-md border border-border bg-bg-primary px-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
          {query.length >= 1 && districts.length > 0 && (
            <ul className="absolute z-50 mt-1 w-full max-w-md bg-bg-primary border border-border rounded-md shadow-lg">
              {districts.slice(0, 10).map((d: { id: number; name: string }) => (
                <li key={d.id} className="px-3 py-2 text-sm hover:bg-bg-tertiary cursor-pointer">
                  {d.name}
                </li>
              ))}
            </ul>
          )}
        </div>

        <nav className="flex items-center gap-2">
          <Link
            to="/about"
            className={cn(
              "px-3 py-2 rounded-md text-sm font-medium transition-colors",
              location.pathname === "/about"
                ? "text-primary bg-primary/10"
                : "text-text-secondary hover:text-text-primary",
            )}
          >
            About
          </Link>
          <a
            href="https://github.com/Aashish-po/nepal-ag-dashboard"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-2 rounded-md text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
          >
            GitHub
          </a>
        </nav>
      </div>
    </header>
  );
}
