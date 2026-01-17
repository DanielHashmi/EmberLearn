// Design tokens extracted from design-system.json
// Used for consistent styling across the application

export const colors = {
  brand: {
    primary: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
      950: '#450a0a',
    },
    secondary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
      950: '#082f49',
    },
    accent: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',
      600: '#9333ea',
      700: '#7e22ce',
      800: '#6b21a8',
      900: '#581c87',
      950: '#3b0764',
    },
  },
  semantic: {
    success: { light: '#10b981', dark: '#34d399', bg: '#d1fae5', text: '#065f46' },
    warning: { light: '#f59e0b', dark: '#fbbf24', bg: '#fef3c7', text: '#92400e' },
    error: { light: '#ef4444', dark: '#f87171', bg: '#fee2e2', text: '#991b1b' },
    info: { light: '#3b82f6', dark: '#60a5fa', bg: '#dbeafe', text: '#1e40af' },
  },
  neutral: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#e5e5e5',
    300: '#d4d4d4',
    400: '#a3a3a3',
    500: '#737373',
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717',
    950: '#0a0a0a',
  },
} as const

export const typography = {
  fontFamily: {
    sans: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    mono: "JetBrains Mono, 'Fira Code', Consolas, Monaco, 'Courier New', monospace",
    display: 'Inter, system-ui, sans-serif',
  },
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
    '5xl': '3rem',
    '6xl': '3.75rem',
    '7xl': '4.5rem',
    '8xl': '6rem',
    '9xl': '8rem',
  },
  fontWeight: {
    thin: '100',
    extralight: '200',
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
    black: '900',
  },
} as const

export const spacing = {
  0: '0px',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
  24: '96px',
  32: '128px',
} as const

export const borderRadius = {
  none: '0px',
  sm: '0.125rem',
  base: '0.25rem',
  md: '0.375rem',
  lg: '0.5rem',
  xl: '0.75rem',
  '2xl': '1rem',
  '3xl': '1.5rem',
  full: '9999px',
} as const

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  glow: '0 0 20px rgb(168 85 247 / 0.4)',
  glowIntense: '0 0 20px rgb(168 85 247 / 0.4), 0 0 40px rgb(168 85 247 / 0.2), 0 0 60px rgb(168 85 247 / 0.1)',
} as const

// Mastery level colors and thresholds
export const masteryLevels = {
  beginner: { min: 0, max: 40, color: 'red', label: 'Beginner' },
  learning: { min: 41, max: 70, color: 'yellow', label: 'Learning' },
  proficient: { min: 71, max: 90, color: 'green', label: 'Proficient' },
  mastered: { min: 91, max: 100, color: 'blue', label: 'Mastered' },
} as const

export function getMasteryLevel(score: number) {
  if (score <= 40) return masteryLevels.beginner
  if (score <= 70) return masteryLevels.learning
  if (score <= 90) return masteryLevels.proficient
  return masteryLevels.mastered
}

export function getMasteryColor(score: number): string {
  const level = getMasteryLevel(score)
  const colorMap = {
    red: colors.brand.primary[500],
    yellow: colors.semantic.warning.light,
    green: colors.semantic.success.light,
    blue: colors.brand.secondary[500],
  }
  return colorMap[level.color as keyof typeof colorMap]
}

// Python curriculum topics
export const pythonTopics = [
  { id: 1, name: 'Basics', slug: 'basics', icon: '📚', description: 'Variables, Data Types, Input/Output' },
  { id: 2, name: 'Control Flow', slug: 'control-flow', icon: '🔀', description: 'Conditionals, Loops, Break/Continue' },
  { id: 3, name: 'Data Structures', slug: 'data-structures', icon: '📦', description: 'Lists, Tuples, Dictionaries, Sets' },
  { id: 4, name: 'Functions', slug: 'functions', icon: '⚡', description: 'Defining Functions, Parameters, Scope' },
  { id: 5, name: 'OOP', slug: 'oop', icon: '🏗️', description: 'Classes, Objects, Inheritance' },
  { id: 6, name: 'Files', slug: 'files', icon: '📁', description: 'Reading/Writing, CSV, JSON' },
  { id: 7, name: 'Errors', slug: 'errors', icon: '🐛', description: 'Try/Except, Custom Exceptions' },
  { id: 8, name: 'Libraries', slug: 'libraries', icon: '📦', description: 'Packages, APIs, Virtual Environments' },
] as const

export type PythonTopic = typeof pythonTopics[number]
