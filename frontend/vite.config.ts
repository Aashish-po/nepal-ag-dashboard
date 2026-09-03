import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  // ponytail: split d3-geo (Map) and Recharts-heavy pages (Compare, Forecasts)
  // into their own chunks so the initial app bundle stays under 500KB.
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('d3-geo')) return 'vendor-d3'
          if (id.includes('recharts')) return 'vendor-recharts'
          return undefined
        },
      },
    },
  },
})
