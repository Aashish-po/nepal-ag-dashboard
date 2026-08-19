import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'
import { Table, TableBody, TableRow, TableCell } from '@/shadcn/table'

const mockData = [
  { year: 2018, production: 4200, revenue: 12500000 }, { year: 2019, production: 4800, revenue: 14400000 },
  { year: 2020, production: 5100, revenue: 15300000 }, { year: 2021, production: 5500, revenue: 17600000 },
  { year: 2022, production: 5900, revenue: 18880000 }, { year: 2023, production: 6200, revenue: 19840000 },
  { year: 2024, production: 6800, revenue: 21760000 },
]

const districtData = [
  { district: 'Ilam', production: 1850, share: 27.2, revenue: 5920000 },
  { district: 'Panchthar', production: 1420, share: 20.9, revenue: 4544000 },
  { district: 'Tehrathum', production: 980, share: 14.4, revenue: 3136000 },
  { district: 'Sankhuwasabha', production: 720, share: 10.6, revenue: 2304000 },
  { district: 'Bhojpur', production: 540, share: 7.9, revenue: 1728000 },
]

export function ExportCrops() {
  const [selectedCrop, setSelectedCrop] = useState('cardamom')

  const handleExport = () => {
    alert('Download report triggered')
  }

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Export Crops</h1>
        <Button variant="outline" onClick={handleExport}>
          Download Report
        </Button>
      </div>

      <div className="flex gap-2 mb-6">
        {['cardamom', 'ginger', 'tea'].map((crop) => (
          <Button
            key={crop}
            variant={selectedCrop === crop ? 'default' : 'outline'}
            onClick={() => setSelectedCrop(crop)}
            className="capitalize"
          >
            {crop}
          </Button>
        ))}
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Production Trend (MT)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
              <XAxis dataKey="year" stroke="var(--color-text-muted)" fontSize={12} />
              <YAxis stroke="var(--color-text-muted)" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-bg-primary)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="production" stroke="var(--color-warning)" strokeWidth={2} name="Production (MT)" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-text-secondary">Avg Price</p>
            <p className="text-2xl font-bold mt-1">$8,450 / MT</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-text-secondary">Est. Total Revenue</p>
            <p className="text-2xl font-bold mt-1">$21.8M / year</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-text-secondary">Peak Export</p>
            <p className="text-2xl font-bold mt-1">Sept–Dec</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top Producing Districts</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableBody>
              {districtData.map((item, idx) => (
                <TableRow key={item.district}>
                  <TableCell className="font-medium">#{idx + 1} {item.district}</TableCell>
                  <TableCell>{item.production.toLocaleString()} MT</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary text-primary-foreground hover:bg-primary/80">
                      {item.share}%
                    </span>
                  </TableCell>
                  <TableCell>${item.revenue.toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
