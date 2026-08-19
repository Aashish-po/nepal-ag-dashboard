import { useState } from 'react'
import { ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area } from 'recharts'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'
import { TableSkeleton } from '@/components/Loading'

const forecastData = [
  { month: 'Jan 2024', historical: 3200, forecast: null, lower: null, upper: null },
  { month: 'Feb 2024', historical: 3250, forecast: null, lower: null, upper: null },
  { month: 'Mar 2024', historical: 3280, forecast: null, lower: null, upper: null },
  { month: 'Apr 2024', historical: 3350, forecast: null, lower: null, upper: null },
  { month: 'May 2024', historical: 3420, forecast: null, lower: null, upper: null },
  { month: 'Jun 2024', forecast: 3480, lower: 3400, upper: 3560 },
  { month: 'Jul 2024', forecast: 3520, lower: 3430, upper: 3610 },
  { month: 'Aug 2024', forecast: 3550, lower: 3450, upper: 3650 },
  { month: 'Sep 2024', forecast: 3580, lower: 3460, upper: 3700 },
  { month: 'Oct 2024', forecast: 3600, lower: 3470, upper: 3730 },
]

const diagnostics = {
  model: 'ARIMA(1,1,1)',
  rmse: '124 kg/ha',
  recommendation: 'Growth trend',
}

export function Forecasts() {
  const [monthsAhead, setMonthsAhead] = useState(12)

  const handleExport = () => {
    alert('Download Excel triggered')
  }

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Forecasts</h1>
        <Button variant="outline" onClick={handleExport}>
          Download Excel
        </Button>
      </div>

      <div className="flex gap-2 mb-6">
        {[12, 24, 36].map((months) => (
          <Button
            key={months}
            variant={monthsAhead === months ? 'default' : 'outline'}
            onClick={() => setMonthsAhead(months)}
          >
            {months} months
          </Button>
        ))}
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Yield Forecast with 95% Confidence Interval</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <ComposedChart data={forecastData}>
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
              <Legend />
              <Line type="monotone" dataKey="historical" stroke="var(--color-text-primary)" strokeWidth={2} name="Historical" connectNulls={false} />
              <Line type="monotone" dataKey="forecast" stroke="var(--color-secondary)" strokeWidth={2} name="Forecast" connectNulls={false} />
              <Area type="monotone" dataKey="upper" stroke="none" fill="var(--color-secondary)" fillOpacity={0.15} name="Upper CI" connectNulls={false} />
              <Area type="monotone" dataKey="lower" stroke="none" fill="var(--color-secondary)" fillOpacity={0.05} name="Lower CI" connectNulls={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-text-secondary">Model</p>
            <p className="text-lg font-bold mt-1">{diagnostics.model}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-text-secondary">Historical RMSE</p>
            <p className="text-lg font-bold mt-1">{diagnostics.rmse}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-text-secondary">Recommendation</p>
            <p className="text-lg font-bold mt-1 text-primary">{diagnostics.recommendation}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Forecast Table</CardTitle>
        </CardHeader>
        <CardContent>
          <TableSkeleton rows={5} />
        </CardContent>
      </Card>
    </div>
  )
}
