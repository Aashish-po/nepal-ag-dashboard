import { useState } from 'react'
import { MapPin, Navigation } from 'lucide-react'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'
import { cn } from '@/lib/utils'

const mockDistricts = [
  { id: 1, name: 'Kathmandu', province: 'Bagmati', avgYield: 3600, topCrop: 'Rice', score: 72 },
  { id: 2, name: 'Lalitpur', province: 'Bagmati', avgYield: 3400, topCrop: 'Rice', score: 65 },
  { id: 3, name: 'Bhaktapur', province: 'Bagmati', avgYield: 3350, topCrop: 'Rice', score: 58 },
  { id: 4, name: 'Pokhara', province: 'Gandaki', avgYield: 3100, topCrop: 'Maize', score: 45 },
  { id: 5, name: 'Biratnagar', province: 'Koshi', avgYield: 2900, topCrop: 'Wheat', score: 38 },
  { id: 6, name: 'Birgunj', province: 'Madhesh', avgYield: 2700, topCrop: 'Rice', score: 32 },
]

export function Map() {
  const [selectedDistrict, setSelectedDistrict] = useState<(typeof mockDistricts)[0] | null>(null)

  const getScoreColor = (score: number) => {
    if (score >= 60) return 'var(--color-primary)'
    if (score >= 40) return 'var(--color-warning)'
    return 'var(--color-error)'
  }

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <h1 className="text-h1 font-bold mb-6">District Map</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Nepal District Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2">
                {mockDistricts.map((district) => (
                  <button
                    key={district.id}
                    onClick={() => setSelectedDistrict(district)}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 rounded-md border transition-colors text-sm',
                      selectedDistrict?.id === district.id
                        ? 'border-primary bg-primary/10'
                        : 'border-border-primary hover:bg-bg-tertiary'
                    )}
                  >
                    <MapPin className="w-4 h-4" style={{ color: getScoreColor(district.score) }} />
                    {district.name}
                  </button>
                ))}
              </div>
              <p className="text-sm text-text-muted mt-2">
                Map visualization requires GeoJSON data. Click a district to view details.
              </p>
            </div>
          </CardContent>
        </Card>

        {selectedDistrict && (
          <Card>
            <CardHeader>
              <CardTitle>{selectedDistrict.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-text-secondary">
                  <Navigation className="w-4 h-4" />
                  {selectedDistrict.province}
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Avg Yield</p>
                  <p className="text-xl font-bold">{selectedDistrict.avgYield.toLocaleString()} kg/ha</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Top Crop</p>
                  <p className="text-xl font-bold">{selectedDistrict.topCrop}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Commercialization Score</p>
                  <p className="text-xl font-bold">{selectedDistrict.score} / 100</p>
                </div>
                <Button variant="outline" className="w-full" onClick={() => setSelectedDistrict(null)}>
                  Close Panel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
