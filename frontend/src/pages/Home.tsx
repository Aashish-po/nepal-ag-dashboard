import { TrendingUp, MapPin, BarChart3, Cloud, Sprout, DollarSign, Globe } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/shadcn/card'

export function Home() {
  const features = [
    { title: 'Yield Analysis', description: 'Analyze crop yields across Nepal districts', icon: BarChart3, href: '/yields', color: 'text-primary' },
    { title: 'Climate Intelligence', description: 'Rainfall, temperature, and solar data', icon: Cloud, href: '/climate', color: 'text-secondary' },
    { title: 'Yield-Climate Correlation', description: 'Understand how climate affects yields', icon: TrendingUp, href: '/correlation', color: 'text-chart-3' },
    { title: 'Export Crops', description: 'Cardamom, ginger, tea production & revenue', icon: DollarSign, href: '/export-crops', color: 'text-chart-5' },
    { title: 'Commercialization', description: 'Subsistence vs. commercial farming gap', icon: Sprout, href: '/commercialization', color: 'text-success' },
    { title: 'Forecasts', description: '12-36 month yield predictions with CI', icon: TrendingUp, href: '/forecasts', color: 'text-secondary' },
    { title: 'District Map', description: 'Interactive geospatial explorer', icon: MapPin, href: '/map', color: 'text-primary' },
    { title: 'Compare Districts', description: 'Side-by-side yield trends', icon: Globe, href: '/compare', color: 'text-chart-6' },
  ]

  const stats = [
    { label: 'Districts', value: '77' },
    { label: 'Crops tracked', value: '35+' },
    { label: 'Data range', value: '2014-2024' },
    { label: 'Climate records', value: '10+ years' },
  ]

  return (
    <div className="max-w-[1400px] mx-auto p-6 space-y-8">
      <section className="text-center py-12">
        <h1 className="text-h1 font-bold mb-4 text-balance">
          Analyze agricultural productivity across Nepal
        </h1>
        <p className="text-lg text-text-secondary max-w-2xl mx-auto mb-8 text-balance">
          Data-driven insights on crop yields, climate patterns, export potential, and forecasts for all 77 districts.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link to="/yields">
            <Button size="lg">Explore Yields</Button>
          </Link>
          <Link to="/forecasts">
            <Button size="lg" variant="secondary">View Forecasts</Button>
          </Link>
          <Link to="/about">
            <Button size="lg" variant="outline">Learn More</Button>
          </Link>
        </div>
      </section>

      <section>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat) => (
            <Card key={stat.label}>
              <CardContent className="pt-6 text-center">
                <p className="text-2xl font-bold text-primary">{stat.value}</p>
                <p className="text-sm text-text-secondary mt-1">{stat.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-h2 font-bold mb-6">Featured Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <Link key={feature.title} to={feature.href}>
                <Card className="h-full transition-shadow hover:shadow-lg">
                  <CardHeader>
                    <div className={`w-10 h-10 rounded-lg bg-bg-secondary flex items-center justify-center ${feature.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <CardTitle className="text-h4">{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                </Card>
              </Link>
            )
          })}
        </div>
      </section>
    </div>
  )
}
