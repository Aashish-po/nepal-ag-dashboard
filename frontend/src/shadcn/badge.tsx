import * as React from 'react'
import { cn } from '@/lib/utils'

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'outline'
}

const badgeVariants: Record<string, string> = {
  default: 'border-transparent bg-primary text-white',
  success: 'border-transparent bg-success text-white',
  warning: 'border-transparent bg-warning text-white',
  error: 'border-transparent bg-error text-white',
  outline: 'text-text-primary border-border-primary',
}

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
        badgeVariants[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }
