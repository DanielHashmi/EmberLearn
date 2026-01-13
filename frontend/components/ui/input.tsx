'use client'

import * as React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/src_lib/utils'

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
  icon?: React.ReactNode
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, icon, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false)

    return (
      <motion.div 
        className="relative"
        animate={{
          boxShadow: isFocused && !error
            ? '0 0 20px rgba(168, 85, 247, 0.15)'
            : '0 0 0px rgba(168, 85, 247, 0)',
        }}
        transition={{ duration: 0.2 }}
        style={{ borderRadius: '0.75rem' }}
      >
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground z-10">
            {icon}
          </div>
        )}
        <input
          type={type}
          className={cn(
            'flex h-11 w-full rounded-xl border bg-background/50 backdrop-blur-sm px-4 py-2 text-sm transition-all duration-300',
            'placeholder:text-muted-foreground',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            'disabled:cursor-not-allowed disabled:opacity-50',
            error
              ? 'border-destructive focus:ring-destructive/50'
              : 'border-input focus:border-accent focus:ring-accent/20',
            icon && 'pl-10',
            className
          )}
          ref={ref}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />
      </motion.div>
    )
  }
)
Input.displayName = 'Input'

export { Input }
