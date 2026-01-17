'use client'

import { motion } from 'framer-motion'

interface GlowBackgroundProps {
  variant?: 'default' | 'subtle' | 'intense'
  className?: string
}

export function GlowBackground({ variant = 'default', className = '' }: GlowBackgroundProps) {
  const intensityMap = {
    subtle: { opacity: 0.15, blur: 100 },
    default: { opacity: 0.25, blur: 120 },
    intense: { opacity: 0.35, blur: 150 },
  }

  const { opacity, blur } = intensityMap[variant]

  return (
    <div className={`fixed inset-0 -z-10 overflow-hidden ${className}`}>
      {/* Base gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-background" />
      
      {/* Animated gradient orbs */}
      <motion.div
        className="absolute -top-40 -right-40 w-96 h-96 rounded-full"
        style={{
          background: `radial-gradient(circle, rgba(168, 85, 247, ${opacity}) 0%, transparent 70%)`,
          filter: `blur(${blur}px)`,
        }}
        animate={{
          x: [0, 50, 0],
          y: [0, 30, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      
      <motion.div
        className="absolute top-1/3 -left-40 w-80 h-80 rounded-full"
        style={{
          background: `radial-gradient(circle, rgba(239, 68, 68, ${opacity}) 0%, transparent 70%)`,
          filter: `blur(${blur}px)`,
        }}
        animate={{
          x: [0, -30, 0],
          y: [0, 50, 0],
          scale: [1, 1.15, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 2,
        }}
      />
      
      <motion.div
        className="absolute bottom-20 right-1/4 w-72 h-72 rounded-full"
        style={{
          background: `radial-gradient(circle, rgba(14, 165, 233, ${opacity}) 0%, transparent 70%)`,
          filter: `blur(${blur}px)`,
        }}
        animate={{
          x: [0, 40, 0],
          y: [0, -40, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 4,
        }}
      />
      
      <motion.div
        className="absolute top-2/3 left-1/3 w-64 h-64 rounded-full"
        style={{
          background: `radial-gradient(circle, rgba(168, 85, 247, ${opacity * 0.7}) 0%, transparent 70%)`,
          filter: `blur(${blur}px)`,
        }}
        animate={{
          x: [0, -20, 0],
          y: [0, -30, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 22,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 6,
        }}
      />

      {/* Noise texture overlay for depth */}
      <div 
        className="absolute inset-0 opacity-[0.015]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Grid pattern overlay */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px',
        }}
      />
    </div>
  )
}
