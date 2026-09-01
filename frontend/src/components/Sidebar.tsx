'use client'

import { useState } from 'react'
import { Menu, X, Home, BarChart3, Cloud, GitCompare, Sprout, TrendingUp, Map, Globe, Info } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'

const navItems = [
  { label: 'Home', href: '/', icon: Home },
  { label: 'Yields', href: '/yields', icon: BarChart3 },
  { label: 'Climate', href: '/climate', icon: Cloud },
  { label: 'Correlation', href: '/correlation', icon: GitCompare },
  { label: 'Export Crops', href: '/export-crops', icon: Sprout },
  { label: 'Commercialization', href: '/commercialization', icon: TrendingUp },
  { label: 'Forecasts', href: '/forecasts', icon: TrendingUp },
  { label: 'Map', href: '/map', icon: Map },
  { label: 'Compare', href: '/compare', icon: Globe },
  { label: 'About', href: '/about', icon: Info },
]

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 btn btn-outline md:hidden"
        aria-label="Toggle sidebar"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={cn(
          'fixed top-0 left-0 h-screen bg-bg-secondary border-r border-border-primary z-40 transition-transform duration-300',
          'w-70',
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        <div className="flex flex-col h-full">
          <div className="p-4 border-b border-border-light">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
                <Sprout className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-lg leading-tight">Nepal Ag</h1>
                <p className="text-xs text-text-secondary">Intelligence Dashboard</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 overflow-y-auto p-3">
            <ul className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href
                return (
                  <li key={item.href}>
                    <Link
                      to={item.href}
                      onClick={() => setIsOpen(false)}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-primary text-white'
                          : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                      )}
                    >
                      <Icon className="w-5 h-5" />
                      {item.label}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>

          <div className="p-4 border-t border-border-light">
            <p className="text-xs text-text-muted text-center">
              Phase 1 · v0.1.0
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
