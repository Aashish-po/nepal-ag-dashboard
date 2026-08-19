import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'
import { TableSkeleton } from '@/components/Loading'
import { formatCubicMeters } from '@/lib/utils'

const mockData = [
  { year: 2018, yield: 3200, district: 'Kathmandu' },
  { year: 2019, yield: 3350, district: 'Kathmandu' },
  { year: 2020, yield: 3280, district: 'Kathmandu' },
  { year: 2021, yield: 3420, district: 'Kathmandu' },
  { year: 2022, yield: 3510, district: 'Kathmandu' },
  { year: 2023, yield: 3480, district: 'Kathmandu' },
  { year: 2024, yield: 3600, district: 'Kathmandu' },
]

export function Yields() {
  const handleExport = () => {
    alert('Export CSV triggered')
  }

  const stats = [
    { label: 'Average Yield', value: '3,486 kg/ha' },
    { label: 'Highest', value: '3,600 kg/ha' },
    { label: 'Lowest', value: '3,200 kg/ha' },
    { label: 'Volatility (σ)', value: '125 kg/ha' },
  ]

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Yield Analysis</h1>
        <Button variant="outline" onClick={handleExport}>
          Export CSV
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="pt-6">
              <p className="text-sm text-text-secondary">{stat.label}</p>
              <p className="text-2xl font-bold mt-1">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Yield Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
              <XAxis dataKey="year" stroke="var(--color-text-muted)" fontSize={12} />
              <YAxis stroke="var(--color-text-muted)" fontSize={12} tickFormatter={formatCubicMeters} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-bg-primary)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="yield" stroke="var(--color-primary)" strokeWidth={2} name="Yield (kg/ha)" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <TableSkeleton rows={5} />
    </div>
  )
}
