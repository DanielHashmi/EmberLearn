'use client'

import * as React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/src_lib/utils'
import { getMasteryLevel } from '@/src_lib/design-tokens'

interface ProgressProps {
  value: number
  max?: number
  className?: string
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

export function Progress({
  value,
  max = 100,
  className,
  showLabel = false,
  size = 'md',
  animated = true,
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  const level = getMasteryLevel(percentage)

  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  }

  const colorClasses = {
    red: 'from-red-500 to-red-400',
    yellow: 'from-yellow-500 to-yellow-400',
    green: 'from-green-500 to-green-400',
    blue: 'from-blue-500 to-blue-400',
  }

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'w-full rounded-full overflow-hidden bg-muted/30',
          sizeClasses[size]
        )}
      >
        <motion.div
          className={cn(
            'h-full rounded-full bg-gradient-to-r',
            colorClasses[level.color as keyof typeof colorClasses]
          )}
          initial={animated ? { width: 0 } : { width: `${percentage}%` }}
          animate={{ width: `${percentage}%` }}
          transition={{
            duration: animated ? 1 : 0,
            ease: [0, 0, 0.2, 1],
          }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between mt-1.5 text-xs text-muted-foreground">
          <span>{level.label}</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
    </div>
  )
}

// Circular progress ring
interface ProgressRingProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  className?: string
  showValue?: boolean
}

export function ProgressRing({
  value,
  max = 100,
  size = 80,
  strokeWidth = 8,
  className,
  showValue = true,
}: ProgressRingProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  const level = getMasteryLevel(percentage)
  
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (percentage / 100) * circumference

  const colorMap = {
    red: '#ef4444',
    yellow: '#f59e0b',
    green: '#10b981',
    blue: '#0ea5e9',
  }

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-muted/20"
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={colorMap[level.color as keyof typeof colorMap]}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: [0, 0, 0.2, 1] }}
          style={{
            strokeDasharray: circumference,
            filter: `drop-shadow(0 0 6px ${colorMap[level.color as keyof typeof colorMap]}40)`,
          }}
        />
      </svg>
      {showValue && (
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.span
            className="text-lg font-bold"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.3 }}
          >
            {Math.round(percentage)}%
          </motion.span>
        </div>
      )}
    </div>
  )
}
