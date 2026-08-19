import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Button } from '@/shadcn/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/shadcn/card'

const scatterData = [
  { x: 280, y: 3200, month: 'Jun' }, { x: 420, y: 3600, month: 'Jul' }, { x: 380, y: 3550, month: 'Aug' },
  { x: 210, y: 3480, month: 'Sep' }, { x: 65, y: 3300, month: 'Oct' }, { x: 12, y: 3150, month: 'Jan' },
  { x: 145, y: 3400, month: 'May' },
]

const correlationMatrix = [
  { variable: 'Rainfall', coefficient: 0.78, pValue: 0.012, rSquared: 0.61, significant: true },
  { variable: 'Temperature', coefficient: -0.22, pValue: 0.42, rSquared: 0.05, significant: false },
  { variable: 'Solar Radiation', coefficient: 0.35, pValue: 0.28, rSquared: 0.12, significant: false },
]

export function Correlation() {
  return (
    <div className="max-w-[1400px] mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 font-bold">Yield-Climate Correlation</h1>
        <Button variant="outline" onClick={() => alert('Export analysis triggered')}>
          Download Matrix
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Correlation Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {correlationMatrix.map((row) => (
                <div key={row.variable} className="flex items-center gap-4">
                  <div className="w-40 text-sm font-medium">{row.variable}</div>
                  <div className="flex-1 h-8 rounded-md relative overflow-hidden" style={{
                    backgroundColor: row.coefficient > 0 ? 'rgba(46, 125, 50, 0.15)' : 'rgba(229, 57, 53, 0.15)',
                  }}>
                    <div
                      className="absolute inset-y-0 left-0 rounded-md"
                      style={{
                        width: `${Math.abs(row.coefficient) * 100}%`,
                        backgroundColor: row.coefficient > 0 ? 'var(--color-primary)' : 'var(--color-error)',
                      }}
                    />
                    <span className="absolute inset-0 flex items-center justify-center text-sm font-medium">
                      r = {row.coefficient.toFixed(2)}
                    </span>
                  </div>
                  <div className="w-24 text-right text-sm text-text-secondary">p = {row.pValue.toFixed(3)}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Rainfall vs. Yield</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                <XAxis type="number" dataKey="x" name="Rainfall (mm)" stroke="var(--color-text-muted)" fontSize={12} />
                <YAxis type="number" dataKey="y" name="Yield (kg/ha)" stroke="var(--color-text-muted)" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-bg-primary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                  }}
                  cursor={{ strokeDasharray: '3 3' }}
                />
                <Scatter data={scatterData} fill="var(--color-primary)" name="Rainfall vs Yield" />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Summary Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {correlationMatrix.map((row) => (
              <div key={row.variable} className="p-4 bg-bg-secondary rounded-lg">
                <p className="text-sm text-text-secondary">{row.variable}</p>
                <p className="text-xl font-bold mt-1">R² = {row.rSquared.toFixed(2)}</p>
                <p className="text-sm text-text-muted mt-1">
                  {row.significant ? 'Statistically significant' : 'Not significant'} (p = {row.pValue.toFixed(3)})
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
