import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, AreaChart, Area } from 'recharts'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'

const rainfallData = [
  { month: 'Jan', rainfall: 12 }, { month: 'Feb', rainfall: 18 }, { month: 'Mar', rainfall: 35 },
  { month: 'Apr', rainfall: 62 }, { month: 'May', rainfall: 145 }, { month: 'Jun', rainfall: 280 },
  { month: 'Jul', rainfall: 420 }, { month: 'Aug', rainfall: 380 }, { month: 'Sep', rainfall: 210 },
  { month: 'Oct', rainfall: 65 }, { month: 'Nov', rainfall: 18 }, { month: 'Dec', rainfall: 8 },
]

const tempData = [
  { month: 'Jan', min: 8, mean: 14, max: 20 }, { month: 'Feb', min: 10, mean: 16, max: 22 },
  { month: 'Mar', min: 14, mean: 20, max: 26 }, { month: 'Apr', min: 18, mean: 24, max: 30 },
  { month: 'May', min: 20, mean: 26, max: 32 }, { month: 'Jun', min: 22, mean: 27, max: 31 },
  { month: 'Jul', min: 23, mean: 27, max: 30 }, { month: 'Aug', min: 22, mean: 27, max: 30 },
  { month: 'Sep', min: 21, mean: 26, max: 30 }, { month: 'Oct', min: 17, mean: 22, max: 27 },
  { month: 'Nov', min: 13, mean: 18, max: 23 }, { month: 'Dec', min: 9, mean: 14, max: 20 },
]

const solarData = [
  { month: 'Jan', solar: 14 }, { month: 'Feb', solar: 16 }, { month: 'Mar', solar: 19 },
  { month: 'Apr', solar: 21 }, { month: 'May', solar: 22 }, { month: 'Jun', solar: 18 },
  { month: 'Jul', solar: 15 }, { month: 'Aug', solar: 16 }, { month: 'Sep', solar: 18 },
  { month: 'Oct', solar: 19 }, { month: 'Nov', solar: 16 }, { month: 'Dec', solar: 14 },
]

export function Climate() {
  const stats = [
    { label: 'Annual Rainfall', value: '1,583 mm' },
    { label: 'Avg Temperature', value: '22.5°C' },
    { label: 'Monsoon Period', value: 'Jun–Sep' },
  ]

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Climate Intelligence</h1>
        <Button variant="outline" onClick={() => alert('Download CSV triggered')}>
          Download CSV
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="pt-6">
              <p className="text-sm text-text-secondary">{stat.label}</p>
              <p className="text-2xl font-bold mt-1">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Monthly Rainfall</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={rainfallData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                <XAxis dataKey="month" stroke="var(--color-text-muted)" fontSize={12} />
                <YAxis stroke="var(--color-text-muted)" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-bg-primary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                  }}
                />
                <Bar dataKey="rainfall" fill="var(--color-secondary)" radius={[4, 4, 0, 0]} name="Rainfall (mm)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Temperature (Min / Mean / Max)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={tempData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                <XAxis dataKey="month" stroke="var(--color-text-muted)" fontSize={12} />
                <YAxis stroke="var(--color-text-muted)" fontSize={12} unit="°C" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-bg-primary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="min" stroke="var(--color-secondary)" strokeWidth={2} name="Min (°C)" />
                <Line type="monotone" dataKey="mean" stroke="var(--color-primary)" strokeWidth={2} name="Mean (°C)" />
                <Line type="monotone" dataKey="max" stroke="var(--color-error)" strokeWidth={2} name="Max (°C)" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Solar Radiation</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={solarData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                <XAxis dataKey="month" stroke="var(--color-text-muted)" fontSize={12} />
                <YAxis stroke="var(--color-text-muted)" fontSize={12} unit=" MJ/m²" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-bg-primary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                  }}
                />
                <Area type="monotone" dataKey="solar" stroke="var(--color-warning)" fill="var(--color-warning)" fillOpacity={0.3} name="Solar (MJ/m²)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
