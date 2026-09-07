import { clsx, type ClassValue } from 'clsx'

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

export function downloadBlob(blob: Blob, filename: string): void {
  // ponytail: capture URL impl at call-time; happy-dom tears down window before the 100 ms revoke fires
  const U = typeof window !== 'undefined' ? window.URL : globalThis.URL
  const url = U.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  setTimeout(() => {
    try {
      U.revokeObjectURL(url)
    } catch {
      /* empty */
    }
  }, 100)
}
