import {
  TrendingUp,
  MapPin,
  BarChart3,
  Cloud,
  Sprout,
  DollarSign,
  Globe,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/shadcn/button";
import { useQuery } from "@tanstack/react-query";
import { getDistricts, getCrops } from "@/lib/api";

export function Home() {
  const features = [
    {
      title: "Yield Analysis",
      description: "Analyze crop yields across Nepal districts",
      icon: BarChart3,
      href: "/yields",
    },
    {
      title: "Climate Intelligence",
      description: "Rainfall, temperature, and solar data",
      icon: Cloud,
      href: "/climate",
    },
    {
      title: "Yield-Climate Correlation",
      description: "Understand how climate affects yields",
      icon: TrendingUp,
      href: "/correlation",
    },
    {
      title: "Export Crops",
      description: "Cardamom, ginger, tea production & revenue",
      icon: DollarSign,
      href: "/export-crops",
    },
    {
      title: "Commercialization",
      description: "Subsistence vs. commercial farming gap",
      icon: Sprout,
      href: "/commercialization",
    },
    {
      title: "Forecasts",
      description: "12-36 month yield predictions with CI",
      icon: TrendingUp,
      href: "/forecasts",
    },
    {
      title: "District Map",
      description: "Interactive geospatial explorer",
      icon: MapPin,
      href: "/map",
    },
    {
      title: "Compare Districts",
      description: "Side-by-side yield trends",
      icon: Globe,
      href: "/compare",
    },
  ];

  const { data: districtsData } = useQuery({
    queryKey: ["districts"],
    queryFn: () => getDistricts(),
    staleTime: 300000,
  });
  const { data: cropsData } = useQuery({
    queryKey: ["crops"],
    queryFn: () => getCrops(),
    staleTime: 300000,
  });
  const { data: healthData } = useQuery({
    queryKey: ["health"],
    queryFn: () =>
      fetch(
        `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/v1/health`,
      ).then((r) => r.json()),
    staleTime: 300000,
    refetchOnWindowFocus: false,
  });

  const districtCount = districtsData?.districts?.length ?? 77;
  const cropCount = cropsData?.crops?.length ?? 35;

  const stats = [
    { label: "Districts", value: `${districtCount}` },
    { label: "Crops tracked", value: `${cropCount}+` },
    { label: "Data range", value: "2014–2024" },
    { label: "Climate records", value: "10+ years" },
  ];

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Hero — ruled, stamped */}
      <section className="border border-border border-t-4 border-t-accent p-8 md:p-10">
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="font-mono text-[10px] uppercase tracking-widest border border-border px-2 py-1">
            REV 2.6
          </span>
          <span className="font-mono text-[10px] uppercase tracking-widest border border-border px-2 py-1">
            77 DISTS · 35 CROPS · 2014–2024
          </span>
        </div>
        <h1 className="font-black uppercase tracking-tight leading-[0.9] text-[clamp(32px,6vw,56px)]">
          Nepal Agricultural
          <br />
          Intelligence
        </h1>
        <p className="max-w-[60ch] mt-4 font-mono text-xs uppercase tracking-wider text-text-secondary leading-relaxed">
          Analyze agricultural productivity across Nepal — data-driven insights
          on crop yields, climate patterns, export potential, and forecasts for
          all 77 districts.
        </p>
        <div className="flex flex-wrap gap-3 mt-6">
          <Link to="/yields">
            <Button size="lg">Explore Yields</Button>
          </Link>
          <Link to="/forecasts">
            <Button size="lg" variant="secondary">
              View Forecasts
            </Button>
          </Link>
          <Link to="/about">
            <Button size="lg" variant="outline">
              Learn More
            </Button>
          </Link>
        </div>
      </section>

      {/* Telemetry strip — ruled grid */}
      <section className="ruled-grid grid-cols-2 md:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="p-4 text-center">
            <p className="metric">{stat.value}</p>
            <p className="caption mt-1">{stat.label}</p>
          </div>
        ))}
      </section>

      {/* Bento — 1px-gap ink grid */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <div className="h-px flex-1 bg-border" />
          <span className="font-mono text-[10px] uppercase tracking-widest text-text-muted px-1">
            FEATURED INSIGHTS
          </span>
          <div className="h-px flex-1 bg-border" />
        </div>
        <div className="ruled-grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link key={feature.title} to={feature.href} className="group">
                <div className="h-full p-4 border-t-4 border-t-transparent group-hover:border-t-accent transition-colors">
                  <div className="w-10 h-10 border border-border flex items-center justify-center mb-3">
                    <Icon className="w-5 h-5 text-text-primary" />
                  </div>
                  <p className="font-mono text-xs font-bold uppercase tracking-wider">
                    {feature.title}
                  </p>
                  <p className="font-mono text-[11px] uppercase tracking-wider text-text-secondary mt-1 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      <div className="text-center border border-border py-3">
        <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted">
          Data last updated:{" "}
          {healthData?.timestamp
            ? new Date(healthData.timestamp).toLocaleString()
            : "Not yet synchronized"}{" "}
          · Sources: FAOSTAT · POWER · CHIRPS
        </p>
      </div>
    </div>
  );
}
