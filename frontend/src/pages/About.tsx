import {
  BookOpen,
  Database,
  FileText,
  Mail,
  ExternalLink,
  Cpu,
  BarChart3,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";

export function About() {
  return (
    <div className="mx-auto w-full max-w-5xl px-6 py-8">
      <div className="max-w-5xl mx-auto border-b border-border pb-6 mb-10">
        <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mb-2">
          DOCUMENT - REV 2.6
        </p>
        <h1 className="font-black uppercase tracking-tight text-h1">
          About & Methodology
        </h1>
      </div>

      <div className="space-y-6">
        <Card className="border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-4 h-4" />
              About this project
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 leading-relaxed">
            <p className="text-sm text-text-secondary">
              This dashboard shows crop yields, climate records, and forecasts
              for Nepal&apos;s 77 districts. It pulls together FAOSTAT yield
              data, NASA POWER and CHIRPS climate data, and a weekly forecast
              model. Use it to compare districts, check trends, and download the
              underlying CSVs.
            </p>
            <p className="text-sm text-text-secondary">
              Sources and methods are listed below. Data updates weekly. The
              interface meets WCAG 2.1 AA.
            </p>
          </CardContent>
        </Card>

        <Card className="border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Project Statistics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 border border-border">
                <p className="font-mono text-3xl font-bold text-text-primary">
                  77
                </p>
                <p className="font-mono text-xs uppercase tracking-wider text-text-secondary mt-1">
                  Districts
                </p>
              </div>
              <div className="p-4 border border-border">
                <p className="font-mono text-3xl font-bold text-text-primary">
                  35
                </p>
                <p className="font-mono text-xs uppercase tracking-wider text-text-secondary mt-1">
                  Crop Types
                </p>
              </div>
              <div className="p-4 border border-border">
                <p className="font-mono text-3xl font-bold text-text-primary">
                  10
                </p>
                <p className="font-mono text-xs uppercase tracking-wider text-text-secondary mt-1">
                  Years of Data
                </p>
              </div>
              <div className="p-4 border border-border">
                <p className="font-mono text-3xl font-bold text-text-primary">
                  3
                </p>
                <p className="font-mono text-xs uppercase tracking-wider text-text-secondary mt-1">
                  Export Crops
                </p>
              </div>
            </div>
            <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="p-4 border border-border">
                <p className="font-mono text-xs uppercase tracking-wider font-bold text-text-secondary">
                  Weather & Climate Analysis
                </p>
              </div>
              <div className="p-4 border border-border">
                <p className="font-mono text-xs uppercase tracking-wider font-bold text-text-secondary">
                  Statistical Forecast Models
                </p>
              </div>
              <div className="p-4 border border-border">
                <p className="font-mono text-xs uppercase tracking-wider font-bold text-text-secondary">
                  Multiple Open Data Sources
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="w-4 h-4" />
              Technology Stack
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <p className="font-mono text-xs uppercase tracking-widest font-bold text-text-secondary mb-3">
                  Frontend
                </p>
                <ul className="space-y-2 text-sm text-text-secondary">
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> React 19
                    + TypeScript
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" />{" "}
                    TailwindCSS + shadcn/ui
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> Recharts
                    + d3-geo
                  </li>
                </ul>
              </div>
              <div>
                <p className="font-mono text-xs uppercase tracking-widest font-bold text-text-secondary mb-3">
                  Backend
                </p>
                <ul className="space-y-2 text-sm text-text-secondary">
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> FastAPI
                    + Python 3.12
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> Pandas +
                    NumPy
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" />{" "}
                    Statsmodels (ARIMA, ETS)
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" />{" "}
                    GeoPandas
                  </li>
                </ul>
              </div>
              <div>
                <p className="font-mono text-xs uppercase tracking-widest font-bold text-text-secondary mb-3">
                  Data Sources
                </p>
                <ul className="space-y-2 text-sm text-text-secondary">
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> FAOSTAT
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> NASA
                    POWER
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> CHIRPS
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> MoALD
                    Nepal
                  </li>
                </ul>
              </div>
              <div>
                <p className="font-mono text-xs uppercase tracking-widest font-bold text-text-secondary mb-3">
                  Deployment
                </p>
                <ul className="space-y-2 text-sm text-text-secondary">
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> Vercel
                    (Frontend)
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> Render
                    (Backend)
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" /> GitHub
                    Actions (CI/CD)
                  </li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-4 h-4" />
              Data Sources
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-0">
            {[
              {
                name: "FAOSTAT",
                desc: "Crop production and yield data (2014–2024)",
                href: "https://www.fao.org/faostat",
              },
              {
                name: "NASA POWER",
                desc: "Temperature and solar radiation data",
                href: "https://power.larc.nasa.gov",
              },
              {
                name: "CHIRPS",
                desc: "Rainfall data (2014–2024)",
                href: "https://www.chc.ucsb.edu/research/chirps",
              },
              {
                name: "MoALD Nepal",
                desc: "Ministry of Agriculture and Livestock Development",
                href: "https://www.moald.gov.np",
              },
            ].map((src) => (
              <div
                key={src.name}
                className="flex items-start justify-between border-b border-border-light py-3 last:border-0"
              >
                <div>
                  <p className="font-mono text-xs uppercase tracking-wider font-bold">
                    {src.name}
                  </p>
                  <p className="font-mono text-[11px] uppercase tracking-wider text-text-secondary">
                    {src.desc}
                  </p>
                </div>
                <a
                  href={src.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`Visit ${src.name}`}
                  className="text-text-primary hover:text-accent border border-border px-2 py-1 ml-3 shrink-0"
                >
                  <ExternalLink className="w-4 h-4" aria-hidden="true" />
                </a>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Definitions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-l-2 border-border pl-3">
              <h4 className="font-mono text-xs uppercase tracking-widest font-bold">
                Yield (kg/ha)
              </h4>
              <p className="font-mono text-[11px] uppercase tracking-wider text-text-secondary mt-1">
                The amount of crop produced per hectare of harvested land,
                measured in kilograms.
              </p>
            </div>
            <div className="border-l-2 border-border pl-3">
              <h4 className="font-mono text-xs uppercase tracking-widest font-bold">
                Commercialization Score
              </h4>
              <p className="font-mono text-[11px] uppercase tracking-wider text-text-secondary mt-1">
                A 0–100 index combining export area percentage, farm size, and
                export volume. Higher scores indicate greater commercial
                orientation.
              </p>
            </div>
            <div className="border-l-2 border-border pl-3">
              <h4 className="font-mono text-xs uppercase tracking-widest font-bold">
                Confidence Interval (CI)
              </h4>
              <p className="font-mono text-[11px] uppercase tracking-wider text-text-secondary mt-1">
                The range within which we expect the true forecast value to fall
                with 95% probability.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Methodologies
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-l-2 border-border pl-3">
              <h4 className="font-mono text-xs uppercase tracking-widest font-bold">
                Yield Calculation
              </h4>
              <p className="font-mono text-[11px] uppercase tracking-wider text-text-secondary mt-1">
                Yield is computed as production (MT) × 1,000 / area harvested
                (ha). Data quality flags indicate source reliability.
              </p>
            </div>
            <div className="border-l-2 border-border pl-3">
              <h4 className="font-mono text-xs uppercase tracking-widest font-bold">
                Correlation Analysis
              </h4>
              <p className="font-mono text-[11px] uppercase tracking-wider text-text-secondary mt-1">
                Pearson correlation coefficient between climate variables and
                yield, with p-values for significance testing. Lag detection
                identifies delayed effects.
              </p>
            </div>
            <div className="border-l-2 border-border pl-3">
              <h4 className="font-mono text-xs uppercase tracking-widest font-bold">
                Forecast Models
              </h4>
              <p className="font-mono text-[11px] uppercase tracking-wider text-text-secondary mt-1">
                ARIMA and Exponential Smoothing models are trained on historical
                data. Model selection is based on minimum RMSE on a validation
                set.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Contact & Collaboration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <p className="font-mono text-xs uppercase tracking-widest font-bold text-text-secondary">
                  Developer
                </p>
                <div className="space-y-3 font-mono text-sm">
                  <div className="flex items-center gap-3 text-text-secondary">
                    <span className="w-20 text-text-muted">Name</span>
                    <span className="text-text-primary">Aashish Paudel</span>
                  </div>
                  <div className="flex items-center gap-3 text-text-secondary">
                    <span className="w-20 text-text-muted">Education</span>
                    <span>Computer Science , Tribhuvan University</span>
                  </div>
                  <div className="flex items-center gap-3 text-text-secondary">
                    <span className="w-20 text-text-muted">GitHub</span>
                    <a
                      href="https://github.com/Aashish-po"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent hover:underline"
                    >
                      github.com/Aashish-po
                    </a>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <p className="font-mono text-xs uppercase tracking-widest font-bold text-text-secondary">
                  Project
                </p>
                <div className="space-y-3 font-mono text-sm">
                  <div className="flex items-center gap-3 text-text-secondary">
                    <span className="w-20 text-text-muted">Repository</span>
                    <a
                      href="https://github.com/Aashish-po/nepal-ag-dashboard"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent hover:underline"
                    >
                      nepal-ag-dashboard
                    </a>
                  </div>
                  <div className="flex items-center gap-3 text-text-secondary">
                    <span className="w-20 text-text-muted">Issues</span>
                    <a
                      href="https://github.com/Aashish-po/nepal-ag-dashboard/issues"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent hover:underline"
                    >
                      GitHub Issues
                    </a>
                  </div>
                  <div className="flex items-center gap-3 text-text-secondary">
                    <span className="w-20 text-text-muted">Data</span>
                    <span>Contributions welcome</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="pt-4 border-t border-border">
              <p className="font-mono text-xs uppercase tracking-widest font-bold text-text-secondary mb-2">
                Email
              </p>
              <a
                href="mailto:aashishpaudel67@proton.me"
                className="text-text-primary hover:text-accent underline"
              >
                aashishpaudel67@proton.me
              </a>
            </div>
            <div className="pt-4 border-t border-border bg-bg-secondary p-4">
              <p className="font-mono text-xs uppercase tracking-widest font-bold text-text-secondary mb-2">
                Suggested Citation
              </p>
              <p className="font-mono text-[11px] uppercase tracking-wider text-text-muted">
                Paudel, A. (2026).{" "}
                <em className="font-mono not-italic text-text-secondary">
                  Nepal Agricultural Intelligence Dashboard
                </em>{" "}
                (Version 1.0).
                <br />
                Retrieved from:{" "}
                <span className="text-accent">
                  https://nepal-ag-dashboard.vercel.app
                </span>
                <br />
                Source code:{" "}
                <span className="text-accent">
                  https://github.com/Aashish-po/nepal-ag-dashboard
                </span>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
