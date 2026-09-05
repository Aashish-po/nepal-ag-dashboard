"use client";

import { useState } from "react";
import {
  Menu,
  X,
  Home,
  BarChart3,
  Cloud,
  GitCompare,
  Sprout,
  LineChart,
  Map,
  Layers,
  Info,
  Activity,
} from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

const navGroups = [
  {
    label: "ANALYZE",
    items: [
      { label: "Yields", href: "/yields", icon: BarChart3 },
      { label: "Climate", href: "/climate", icon: Cloud },
      { label: "Correlation", href: "/correlation", icon: GitCompare },
      { label: "Forecasts", href: "/forecasts", icon: LineChart },
    ],
  },
  {
    label: "EXPLORE",
    items: [
      { label: "Map", href: "/map", icon: Map },
      { label: "Compare", href: "/compare", icon: Layers },
      { label: "Export Crops", href: "/export-crops", icon: Sprout },
      {
        label: "Commercialization",
        href: "/commercialization",
        icon: Activity,
      },
    ],
  },
  {
    label: "SYSTEM",
    items: [
      { label: "Home", href: "/", icon: Home },
      { label: "About", href: "/about", icon: Info },
    ],
  },
];

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 btn btn-outline lg:hidden"
        aria-label="Toggle sidebar"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed top-0 left-0 h-screen bg-bg-secondary border-r border-border z-40 transition-transform duration-300",
          "w-72",
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex flex-col h-full">
          <div className="p-4 border-b border-border-light">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-text-primary border border-border flex items-center justify-center shrink-0">
                <Sprout className="w-6 h-6 text-bg-primary" />
              </div>
              <div>
                <h1 className="font-black text-sm uppercase tracking-tight leading-tight">
                  Nepal Ag
                </h1>
                <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted">
                  Intelligence Dashboard - REV 2.6
                </p>
              </div>
            </div>
          </div>

          <nav className="flex-1 overflow-y-auto p-3 space-y-5">
            {navGroups.map((group) => (
              <div key={group.label}>
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-px flex-1 bg-border-light" />
                  <span className="font-mono text-[10px] uppercase tracking-widest text-text-muted px-1">
                    {group.label}
                  </span>
                  <div className="h-px flex-1 bg-border-light" />
                </div>
                <ul className="space-y-1">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.href;
                    return (
                      <li key={item.href}>
                        <Link
                          to={item.href}
                          onClick={() => setIsOpen(false)}
                          className={cn(
                            "flex items-center gap-3 px-3 py-2 text-xs font-mono uppercase tracking-wider transition-colors border-l-[3px]",
                            isActive
                              ? "bg-bg-tertiary text-text-primary border-accent"
                              : "text-text-secondary hover:bg-bg-tertiary hover:text-text-primary border-transparent",
                          )}
                        >
                          <Icon className="w-4 h-4 shrink-0" />
                          <span className="bracket">{item.label}</span>
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </nav>

          <div className="p-3 border-t border-border-light">
            <div className="flex items-center justify-center gap-2 font-mono text-[10px] uppercase tracking-widest text-text-muted">
              <span className="w-2 h-2 bg-accent inline-block" aria-hidden />
              V1.0.0
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
