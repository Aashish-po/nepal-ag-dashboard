import { clsx, type ClassValue } from 'clsx'
import { format as formatDateFns } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatNumber(value: number, decimals: number = 0): string {
  if (value == null || Number.isNaN(value)) return '-'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatPercent(value: number, decimals: number = 1): string {
  if (value == null || Number.isNaN(value)) return '-'
  return `${formatNumber(value, decimals)}%`
}

export function formatDate(date: string | Date, pattern: string = 'MMM yyyy'): string {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  if (Number.isNaN(d.getTime())) return '-'
  try {
    return formatDateFns(d, pattern)
  } catch {
    return d.toISOString()
  }
}

export function formatCubicMeters(value: number): string {
  if (value == null || Number.isNaN(value)) return '-'
  return `${formatNumber(value)} kg/ha`
}

export function truncate(text: string, maxLength: number = 50): string {
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  // Clean up after download starts
  setTimeout(() => window.URL.revokeObjectURL(url), 100)
}
