// Framer Motion animation presets for consistent animations
// Based on design-system.json animation specifications

import { Variants, Transition } from 'framer-motion'

// Spring configurations
export const springs = {
  default: { type: 'spring', stiffness: 300, damping: 28 } as Transition,
  gentle: { type: 'spring', stiffness: 200, damping: 30 } as Transition,
  bouncy: { type: 'spring', stiffness: 400, damping: 20 } as Transition,
  slow: { type: 'spring', stiffness: 100, damping: 25 } as Transition,
  snappy: { type: 'spring', stiffness: 500, damping: 30 } as Transition,
}

// Duration presets (in seconds)
export const durations = {
  instant: 0,
  fast: 0.15,
  normal: 0.3,
  slow: 0.5,
  slower: 0.8,
  slowest: 1.2,
}

// Easing presets
export const easings = {
  linear: 'linear',
  easeIn: [0.4, 0, 1, 1],
  easeOut: [0, 0, 0.2, 1],
  easeInOut: [0.4, 0, 0.2, 1],
  spring: [0.34, 1.56, 0.64, 1],
  bounce: [0.68, -0.55, 0.265, 1.55],
}

// Fade animations
export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
}

export const fadeInUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
}

export const fadeInDown: Variants = {
  initial: { opacity: 0, y: -20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
}

export const fadeInLeft: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
}

export const fadeInRight: Variants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
}

// Scale animations
export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
}

export const scaleInBounce: Variants = {
  initial: { opacity: 0, scale: 0.8 },
  animate: { 
    opacity: 1, 
    scale: 1,
    transition: springs.bouncy,
  },
  exit: { opacity: 0, scale: 0.8 },
}

// Slide animations
export const slideUp: Variants = {
  initial: { y: '100%' },
  animate: { y: 0 },
  exit: { y: '100%' },
}

export const slideDown: Variants = {
  initial: { y: '-100%' },
  animate: { y: 0 },
  exit: { y: '-100%' },
}

export const slideLeft: Variants = {
  initial: { x: '100%' },
  animate: { x: 0 },
  exit: { x: '-100%' },
}

export const slideRight: Variants = {
  initial: { x: '-100%' },
  animate: { x: 0 },
  exit: { x: '100%' },
}

// Stagger container for children animations
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.1,
    },
  },
  exit: {
    transition: {
      staggerChildren: 0.04,
      staggerDirection: -1,
    },
  },
}

export const staggerContainerFast: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.03,
      delayChildren: 0.05,
    },
  },
}

export const staggerContainerSlow: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
}

// Stagger item (use with staggerContainer)
export const staggerItem: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: springs.default,
  },
  exit: { opacity: 0, y: -10 },
}

// Page transition variants
export const pageTransition: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.4,
      ease: easings.easeOut,
    },
  },
  exit: { 
    opacity: 0, 
    y: -20,
    transition: {
      duration: 0.3,
      ease: easings.easeIn,
    },
  },
}

// Tab content transition (for extensive layout animations)
export const tabContent: Variants = {
  initial: { opacity: 0, x: 20, scale: 0.98 },
  animate: { 
    opacity: 1, 
    x: 0, 
    scale: 1,
    transition: springs.default,
  },
  exit: { 
    opacity: 0, 
    x: -20, 
    scale: 0.98,
    transition: { duration: 0.2 },
  },
}

// Card hover animation
export const cardHover = {
  scale: 1.02,
  y: -4,
  transition: springs.gentle,
}

export const cardTap = {
  scale: 0.98,
  transition: { duration: 0.1 },
}

// Button animations
export const buttonHover = {
  scale: 1.05,
  transition: springs.snappy,
}

export const buttonTap = {
  scale: 0.95,
  transition: { duration: 0.1 },
}

// Glow pulse animation
export const glowPulse: Variants = {
  initial: { 
    boxShadow: '0 0 20px rgba(168, 85, 247, 0.4)' 
  },
  animate: {
    boxShadow: [
      '0 0 20px rgba(168, 85, 247, 0.4)',
      '0 0 40px rgba(168, 85, 247, 0.6)',
      '0 0 20px rgba(168, 85, 247, 0.4)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
}

// Float animation
export const float: Variants = {
  initial: { y: 0 },
  animate: {
    y: [-10, 10, -10],
    transition: {
      duration: 6,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
}

// Rotate animation
export const rotate: Variants = {
  initial: { rotate: 0 },
  animate: {
    rotate: 360,
    transition: {
      duration: 20,
      repeat: Infinity,
      ease: 'linear',
    },
  },
}

// Progress bar animation
export const progressBar = (value: number): Variants => ({
  initial: { width: 0 },
  animate: { 
    width: `${value}%`,
    transition: {
      duration: 1,
      ease: easings.easeOut,
    },
  },
})

// Typing indicator animation
export const typingDot: Variants = {
  initial: { y: 0 },
  animate: {
    y: [-4, 0, -4],
    transition: {
      duration: 0.6,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
}

// Modal/Dialog animations
export const modalOverlay: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
}

export const modalContent: Variants = {
  initial: { opacity: 0, scale: 0.95, y: 20 },
  animate: { 
    opacity: 1, 
    scale: 1, 
    y: 0,
    transition: springs.bouncy,
  },
  exit: { 
    opacity: 0, 
    scale: 0.95, 
    y: 20,
    transition: { duration: 0.2 },
  },
}

// Toast notification animation
export const toast: Variants = {
  initial: { opacity: 0, y: 50, scale: 0.9 },
  animate: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: springs.bouncy,
  },
  exit: { 
    opacity: 0, 
    y: 20, 
    scale: 0.9,
    transition: { duration: 0.2 },
  },
}

// List item animations
export const listItem: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { 
    opacity: 1, 
    x: 0,
    transition: springs.default,
  },
  exit: { 
    opacity: 0, 
    x: 20,
    transition: { duration: 0.2 },
  },
}

// Skeleton loading animation
export const skeleton: Variants = {
  initial: { opacity: 0.5 },
  animate: {
    opacity: [0.5, 1, 0.5],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
}

// Utility function to create delayed variants
export function withDelay(variants: Variants, delay: number): Variants {
  return {
    ...variants,
    animate: {
      ...variants.animate,
      transition: {
        ...(typeof variants.animate === 'object' && 'transition' in variants.animate 
          ? variants.animate.transition 
          : {}),
        delay,
      },
    },
  }
}

// Utility function to create custom stagger
export function createStagger(staggerDelay: number = 0.06, initialDelay: number = 0.1): Variants {
  return {
    initial: {},
    animate: {
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: initialDelay,
      },
    },
  }
}
