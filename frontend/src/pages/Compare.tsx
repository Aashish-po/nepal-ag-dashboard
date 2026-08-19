import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'
import { Table, TableBody, TableRow, TableCell } from '@/shadcn/table'
import { formatCubicMeters } from '@/lib/utils'

const mockData = [
  { year: 2018, kathmandu: 3200, nuwakot: 2800, makwanpur: 3100 },
  { year: 2019, kathmandu: 3350, nuwakot: 2900, makwanpur: 3200 },
  { year: 2020, kathmandu: 3280, nuwakot: 2950, makwanpur: 3150 },
  { year: 2021, kathmandu: 3420, nuwakot: 3050, makwanpur: 3300 },
  { year: 2022, kathmandu: 3510, nuwakot: 3100, makwanpur: 3350 },
  { year: 2023, kathmandu: 3480, nuwakot: 3150, makwanpur: 3400 },
  { year: 2024, kathmandu: 3600, nuwakot: 3200, makwanpur: 3450 },
]

const statsRows = [
  { district: 'Kathmandu', avg: 3548, max: 3600, volatility: 125, cagr: 2.1 },
  { district: 'Nuwakot', avg: 2993, max: 3200, volatility: 140, cagr: 2.3 },
  { district: 'Makwanpur', avg: 3279, max: 3450, volatility: 105, cagr: 1.8 },
]

export function Compare() {
  const handleExport = () => {
    alert('Export comparison CSV triggered')
  }

  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Compare Districts</h1>
        <Button variant="outline" onClick={handleExport}>
          Export Comparison
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Trend Comparison</CardTitle>
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
              <Line type="monotone" dataKey="kathmandu" stroke="var(--color-primary)" strokeWidth={2} name="Kathmandu" />
              <Line type="monotone" dataKey="nuwakot" stroke="var(--color-secondary)" strokeWidth={2} name="Nuwakot" />
              <Line type="monotone" dataKey="makwanpur" stroke="var(--color-warning)" strokeWidth={2} name="Makwanpur" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Stats Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableBody>
              {statsRows.map((row) => (
                <TableRow key={row.district}>
                  <TableCell className="font-medium">{row.district}</TableCell>
                  <TableCell>{row.avg.toLocaleString()} kg/ha</TableCell>
                  <TableCell>{row.max.toLocaleString()} kg/ha</TableCell>
                  <TableCell>{row.volatility} kg/ha</TableCell>
                  <TableCell>{row.cagr}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
