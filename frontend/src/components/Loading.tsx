'use client'

import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
  height?: string | number
  width?: string | number
}

export function Loading({ className, height = '20px', width = '100%' }: SkeletonProps) {
  return (
    <div
      className={cn('skeleton', className)}
      style={{ height, width }}
    />
  )
}

export function CardSkeleton() {
  return (
    <div className="card">
      <div className="space-y-3">
        <Loading height="16px" width="60%" />
        <Loading height="24px" width="40%" />
        <Loading height="16px" width="80%" />
      </div>
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="card">
      <Loading height="20px" width="120px" className="mb-4" />
      <div className="space-y-4">
        <div className="flex items-end gap-2 h-[300px]">
          {Array.from({ length: 12 }).map((_, i) => (
            <div
              key={i}
              className="flex-1 bg-bg-tertiary rounded-t"
              style={{ height: `${Math.random() * 60 + 20}%` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="card overflow-hidden">
      <div className="border-b border-border-light pb-3 mb-3">
        <Loading height="18px" width="150px" />
      </div>
      <div className="space-y-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <Loading height="16px" width="25%" />
            <Loading height="16px" width="20%" />
            <Loading height="16px" width="20%" />
            <Loading height="16px" width="15%" />
          </div>
        ))}
      </div>
    </div>
  )
}
