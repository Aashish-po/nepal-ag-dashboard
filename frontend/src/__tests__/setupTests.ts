import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock window.matchMedia for components that use it
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// ResizeObserver mock for chart components (Recharts).
// A plain class, not a vi.fn(): the config's mockReset/restoreMocks would
// otherwise wipe a spy-based mock after the first test, breaking every
// chart-rendering test that runs after it.
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
;(globalThis as any).ResizeObserver = ResizeObserverMock
