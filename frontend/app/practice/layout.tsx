'use client'

import { GlowBackground } from '@/components/shared/glow-background'

export default function PracticeLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen relative pt-20">
      <GlowBackground />
      {children}
    </div>
  )
}
