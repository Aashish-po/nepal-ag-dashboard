import { describe, it, expect, vi } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'

// Mock the useApi hook's dependencies are self-contained,
// so we can test it directly by simulating an API call.
import { useApi } from '@/hooks/useApi'

describe('useApi hook', () => {
  it('initial state is idle', () => {
    const mockCall = vi.fn()
    const { result } = renderHook(() => useApi(mockCall))

    expect(result.current.loading).toBe(false)
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('fetches data on execute and sets loading state', async () => {
    const mockData = { id: 1, name: 'Kathmandu' }
    const mockCall = vi.fn().mockResolvedValue(mockData)

    const { result } = renderHook(() => useApi(mockCall))

    let returnedPromise: Promise<unknown> | undefined
    await act(async () => {
      returnedPromise = result.current.execute()
    })

    expect(result.current.loading).toBe(true)

    if (returnedPromise) await returnedPromise

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockData)
    expect(result.current.error).toBeNull()
  })

  it('captures errors on execute', async () => {
    const mockError = new Error('Network error')
    const mockCall = vi.fn().mockRejectedValue(mockError)

    const { result } = renderHook(() => useApi(mockCall))

    let returnedPromise: Promise<unknown> | undefined
    await act(async () => {
      returnedPromise = result.current.execute()
    })

    await expect(returnedPromise).rejects.toThrow('Network error')

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBe('Network error')
    expect(result.current.data).toBeNull()
  })

  it('reset clears data and error', async () => {
    const mockData = { id: 1, name: 'Test' }
    const mockCall = vi.fn().mockResolvedValue(mockData)

    const { result } = renderHook(() => useApi(mockCall))

    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.data).toEqual(mockData)

    await act(async () => {
      result.current.reset()
    })
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
    expect(result.current.loading).toBe(false)
  })
})
