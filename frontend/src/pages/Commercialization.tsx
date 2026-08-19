import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'

const mockHeatmap = [
  { district: 'Kathmandu', score: 72, exportArea: 12.5, subsistence: 76.3, holdingSize: 0.68 },
  { district: 'Lalitpur', score: 65, exportArea: 10.2, subsistence: 78.1, holdingSize: 0.54 },
  { district: 'Bhaktapur', score: 58, exportArea: 9.8, subsistence: 79.4, holdingSize: 0.48 },
  { district: 'Pokhara', score: 45, exportArea: 6.2, subsistence: 85.1, holdingSize: 0.92 },
  { district: 'Biratnagar', score: 38, exportArea: 5.1, subsistence: 88.3, holdingSize: 1.12 },
]

const provincialData = [
  { province: 'Bagmati', score: 65 }, { province: 'Gandaki', score: 48 },
  { province: 'Koshi', score: 42 }, { province: 'Madhesh', score: 35 },
  { province: 'Lumbini', score: 30 },
]

export function Commercialization() {
  const [selectedDistrict, setSelectedDistrict] = useState<(typeof mockHeatmap)[0] | null>(null)

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Commercialization Dashboard</h1>
        <Button variant="outline" onClick={() => alert('Download rankings CSV triggered')}>
          Download Rankings
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Commercialization Scores by District</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={mockHeatmap} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                <XAxis type="number" domain={[0, 100]} stroke="var(--color-text-muted)" fontSize={12} />
                <YAxis type="category" dataKey="district" stroke="var(--color-text-muted)" fontSize={12} width={100} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-bg-primary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                  }}
                />
                <Bar dataKey="score" radius={[0, 4, 4, 0]} name="Score" fill="var(--color-primary)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Provincial Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={provincialData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                <XAxis dataKey="province" stroke="var(--color-text-muted)" fontSize={12} />
                <YAxis domain={[0, 100]} stroke="var(--color-text-muted)" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-bg-primary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                  }}
                />
                <Bar dataKey="score" fill="var(--color-secondary)" radius={[4, 4, 0, 0]} name="Avg Score" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {selectedDistrict && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>{selectedDistrict.district} Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-text-secondary">Score</p>
                <p className="text-xl font-bold">{selectedDistrict.score} / 100</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Export Area</p>
                <p className="text-xl font-bold">{selectedDistrict.exportArea}%</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Subsistence Area</p>
                <p className="text-xl font-bold">{selectedDistrict.subsistence}%</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Avg Holding Size</p>
                <p className="text-xl font-bold">{selectedDistrict.holdingSize} ha</p>
              </div>
            </div>
            <Button variant="outline" className="mt-4" onClick={() => setSelectedDistrict(null)}>
              Close
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
