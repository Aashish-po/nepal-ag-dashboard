import { describe, it, expect } from 'vitest'
import { formatNumber } from '@/lib/utils'

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
