import { describe, it, expect } from 'vitest'
import { formatNumber, formatPercent, truncate } from '@/lib/utils'

describe('utils: formatNumber', () => {
  it('formats plain numbers with commas', () => {
    expect(formatNumber(1234567.89)).toBe('1,234,568')
  })

  it('handles decimals when requested', () => {
    expect(formatNumber(3.14159, 2)).toBe('3.14')
  })

  it('returns dash for null/undefined', () => {
    expect(formatNumber(null as any)).toBe('-')
    expect(formatNumber(undefined as any)).toBe('-')
  })

  it('returns dash for NaN', () => {
    expect(formatNumber(NaN)).toBe('-')
  })
})

describe('utils: formatPercent', () => {
  it('formats percentage values', () => {
    expect(formatPercent(42.5)).toBe('42.5%')
    expect(formatPercent(7)).toBe('7.0%')
  })

  it('returns dash for null/undefined', () => {
    expect(formatPercent(null as any)).toBe('-')
  })
})

describe('utils: truncate', () => {
  it('truncates long strings', () => {
    expect(truncate('hello world', 5)).toBe('hello...')
  })

  it('leaves short strings unchanged', () => {
    expect(truncate('hi', 50)).toBe('hi')
  })

  it('returns empty string for empty input', () => {
    expect(truncate('')).toBe('')
  })
})
