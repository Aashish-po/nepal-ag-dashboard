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
