import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Header } from '@/components/Header'
import { BrowserRouter } from 'react-router-dom'

describe('Header component', () => {
  it('renders brand name', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    )
    expect(screen.getByText('Intelligence')).toBeInTheDocument()
  })

  it('renders About link', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    )
    expect(screen.getByRole('link', { name: /about/i })).toBeInTheDocument()
  })

  it('renders GitHub link', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    )
    expect(screen.getByRole('link', { name: /github/i })).toBeInTheDocument()
  })

  it('renders search input', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    )
    expect(screen.getByPlaceholderText(/search district/i)).toBeInTheDocument()
  })
})
