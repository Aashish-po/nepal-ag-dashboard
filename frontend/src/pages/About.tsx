import { BookOpen, Database, FileText, Mail, ExternalLink } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/shadcn/card";

export function About() {
  return (
    <div className="max-w-180 mx-auto p-6">
      <div className="border-b border-border pb-3 mb-8">
        <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mb-1">DOCUMENT - REV 2.6</p>
        <h1 className="font-black uppercase tracking-tight text-h1">About & Methodology</h1>
      </div>

      <div className="space-y-0 border border-border">
        <Card className="border-0 border-b">
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

        <Card className="border-0 border-b">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-4 h-4" />
              Data Sources
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-0">
            {[
              { name: "FAOSTAT", desc: "Crop production and yield data (2014–2024)", href: "https://www.fao.org/faostat" },
              { name: "NASA POWER", desc: "Temperature and solar radiation data", href: "https://power.larc.nasa.gov" },
              { name: "CHIRPS", desc: "Rainfall data (2014–2024)", href: "https://www.chc.ucsb.edu/research/chirps" },
              { name: "MoALD Nepal", desc: "Ministry of Agriculture and Livestock Development", href: "https://www.moald.gov.np" },
            ].map((src) => (
              <div key={src.name} className="flex items-start justify-between border-b border-border-light py-3 last:border-0">
                <div>
                  <p className="font-mono text-xs uppercase tracking-wider font-bold">{src.name}</p>
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

        <Card className="border-0 border-b">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Definitions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-l-2 border-border pl-3">
              <h4 className="font-mono text-xs uppercase tracking-widest font-bold">Yield (kg/ha)</h4>
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

        <Card className="border-0 border-b">
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

        <Card className="border-0">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Contact & Citation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-text-secondary">
              For questions, feedback, or collaboration inquiries, please reach
              out via GitHub or email.
            </p>
            <p className="font-mono text-[11px] uppercase tracking-wider text-text-muted border border-border p-3">
              To cite this dashboard: Paudel, A. (2026).{" "}
              <em>Nepal Agricultural Intelligence Dashboard</em>. Retrieved from
              https://github.com/aashishpaudel/nepal-ag-dashboard
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
