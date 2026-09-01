"use client";

import { Search } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

export function Header() {
  const location = useLocation();

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
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input
              type="search"
              placeholder="Search districts or crops..."
              className="input pl-10"
            />
          </div>
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
            href="https://github.com"
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
