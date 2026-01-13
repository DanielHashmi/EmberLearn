import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/src_lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default:
          'bg-primary/10 text-primary border border-primary/20',
        secondary:
          'bg-secondary/10 text-secondary border border-secondary/20',
        accent:
          'bg-accent/10 text-accent border border-accent/20',
        success:
          'bg-green-500/10 text-green-500 border border-green-500/20',
        warning:
          'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20',
        error:
          'bg-red-500/10 text-red-500 border border-red-500/20',
        info:
          'bg-blue-500/10 text-blue-500 border border-blue-500/20',
        outline:
          'border border-input bg-transparent',
        glass:
          'glass border-white/10',
      },
      size: {
        default: 'px-2.5 py-0.5 text-xs',
        sm: 'px-2 py-0.5 text-[10px]',
        lg: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
