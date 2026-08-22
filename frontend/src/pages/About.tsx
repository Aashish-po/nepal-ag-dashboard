import { BookOpen, Database, FileText, Mail, ExternalLink } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'

export function About() {
  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <h1 className="text-h1 font-bold mb-8">About & Methodology</h1>

      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              About this project
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-text-secondary leading-relaxed">
            <p>
              The Nepal Agricultural Intelligence Dashboard is a data-driven platform providing
              insights into agricultural productivity across Nepal&apos;s 77 districts. It integrates
              crop yield data, climate records, and predictive models to support evidence-based
              decision making for policymakers, researchers, and development organizations.
            </p>
            <p>
              The dashboard is designed to be intuitive and accessible, following WCAG 2.1 AA
              standards. All data sources are openly documented and regularly updated.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              Data Sources
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-text-secondary">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium text-text-primary">FAOSTAT</p>
                <p className="text-sm">Crop production and yield data (2014–2024)</p>
              </div>
              <a href="https://www.fao.org/faostat" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline flex items-center gap-1">
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium text-text-primary">NASA POWER</p>
                <p className="text-sm">Temperature and solar radiation data</p>
              </div>
              <a href="https://power.larc.nasa.gov" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline flex items-center gap-1">
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium text-text-primary">CHIRPS</p>
                <p className="text-sm">Rainfall data (2014–2024)</p>
              </div>
              <a href="https://www.chc.ucsb.edu/research/chirps" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline flex items-center gap-1">
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium text-text-primary">MoALD Nepal</p>
                <p className="text-sm">Ministry of Agriculture and Livestock Development</p>
              </div>
              <a href="https://www.moald.gov.np" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline flex items-center gap-1">
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Definitions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-text-secondary">
            <div>
              <h4 className="font-semibold text-text-primary">Yield (kg/ha)</h4>
              <p className="text-sm">The amount of crop produced per hectare of harvested land, measured in kilograms.</p>
            </div>
            <div>
              <h4 className="font-semibold text-text-primary">Commercialization Score</h4>
              <p className="text-sm">A 0–100 index combining export area percentage, farm size, and export volume. Higher scores indicate greater commercial orientation.</p>
            </div>
            <div>
              <h4 className="font-semibold text-text-primary">Confidence Interval (CI)</h4>
              <p className="text-sm">The range within which we expect the true forecast value to fall with 95% probability.</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Methodologies
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-text-secondary">
            <div>
              <h4 className="font-semibold text-text-primary">Yield Calculation</h4>
              <p className="text-sm">Yield is computed as production (MT) × 1,000 / area harvested (ha). Data quality flags indicate source reliability.</p>
            </div>
            <div>
              <h4 className="font-semibold text-text-primary">Correlation Analysis</h4>
              <p className="text-sm">Pearson correlation coefficient between climate variables and yield, with p-values for significance testing. Lag detection identifies delayed effects.</p>
            </div>
            <div>
              <h4 className="font-semibold text-text-primary">Forecast Models</h4>
              <p className="text-sm">ARIMA and Exponential Smoothing models are trained on historical data. Model selection is based on minimum RMSE on a validation set.</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="w-5 h-5" />
              Contact & Citation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-text-secondary">
            <p>
              For questions, feedback, or collaboration inquiries, please reach out via GitHub or email.
            </p>
            <p className="text-sm">
              To cite this dashboard: Paudel, A. (2026). <em>Nepal Agricultural Intelligence Dashboard</em>. Retrieved from https://github.com/aashishpaudel/nepal-ag-dashboard
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
