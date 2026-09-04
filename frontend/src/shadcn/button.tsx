import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 font-mono uppercase tracking-wider',
  {
    variants: {
      variant: {
        default: 'bg-accent text-white border border-secondary-dark hover:bg-secondary-dark',
        destructive: 'bg-accent text-white border border-secondary-dark hover:bg-secondary-dark',
        outline: 'border border-border bg-transparent hover:bg-bg-secondary text-text-primary',
        secondary: 'bg-text-primary text-bg-primary border border-text-primary hover:bg-[#1a1a1a]',
        ghost: 'hover:bg-bg-secondary text-text-primary border border-transparent',
        link: 'text-accent underline-offset-4 hover:underline border-0',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 px-3 text-xs',
        lg: 'h-12 px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
