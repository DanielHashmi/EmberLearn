'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export default function LandingPage() {
  return (
    <div className="min-h-screen relative overflow-hidden font-sans">

      {/* Main Content Area */}
      <motion.main
        className="pt-32 pb-20 px-4 md:px-8 max-w-7xl mx-auto"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <div className="flex flex-col md:flex-row items-center gap-12">

          {/* Left Column: Text */}
          <div className="flex-1 text-center md:text-left z-10">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, type: "spring" }}
            >
              <h1 className="text-5xl md:text-8xl font-black mb-6 tracking-tight leading-tight">
                Master <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 animate-gradient-x">
                  Python AI
                </span>
              </h1>

              <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-2xl leading-relaxed">
                The first intelligent tutoring platform that adapts to your unique learning style.
                Built with <span className="font-semibold text-foreground">Glassmorphism</span> technology.
              </p>

              <div className="flex flex-wrap gap-4 justify-center md:justify-start">
                <Link href="/register">
                  <Button size="lg" className="h-14 px-8 rounded-2xl text-lg bg-primary hover:bg-primary/90 shadow-xl shadow-primary/20 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
                    Start Learning
                  </Button>
                </Link>
                <Link href="/chat">
                  <Button variant="glass" size="lg" className="h-14 px-8 rounded-2xl text-lg backdrop-blur-xl border-white/20 hover:bg-white/10 hover:border-white/40 transition-all duration-300">
                    Live Demo
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>

          {/* Right Column: Glass Card Stack */}
          <div className="flex-1 w-full max-w-md md:max-w-xl relative h-[600px] hidden md:block">
            <motion.div
              className="absolute inset-0"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.2 }}
            >
              {/* Floating Cards */}
              <GlassCard
                title="AI Tutor"
                icon="🤖"
                className="absolute top-10 left-10 z-30 w-64 rotate-[-6deg]"
                delay={0.4}
              />
              <GlassCard
                title="Code Editor"
                icon="💻"
                className="absolute top-40 right-0 z-20 w-72 rotate-[3deg]"
                delay={0.6}
              />
              <GlassCard
                title="Analytics"
                icon="📊"
                className="absolute bottom-20 left-20 z-10 w-64 rotate-[-3deg]"
                delay={0.8}
              />
            </motion.div>
          </div>
        </div>
      </motion.main>

      {/* Grid of Features */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <Card variant="glass" className="h-full p-8 hover:bg-glass/20 transition-colors border-white/10">
                <div className="text-5xl mb-6 bg-glass/30 w-16 h-16 flex items-center justify-center rounded-2xl">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  )
}

function GlassCard({ title, icon, className, delay }: { title: string, icon: string, className?: string, delay: number }) {
  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{ scale: 1.05, rotate: 0, zIndex: 50 }}
      className={`p-6 rounded-3xl bg-glass/40 backdrop-blur-xl border border-white/30 shadow-2xl shadow-purple-500/10 ${className}`}
    >
      <div className="flex items-center gap-4 mb-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-white/40 to-white/5 flex items-center justify-center text-2xl shadow-inner">
          {icon}
        </div>
        <div className="h-2 w-24 bg-white/20 rounded-full" />
      </div>
      <h3 className="text-xl font-bold text-foreground mb-2">{title}</h3>
      <div className="space-y-2">
        <div className="h-2 w-full bg-white/10 rounded-full" />
        <div className="h-2 w-3/4 bg-white/10 rounded-full" />
      </div>
    </motion.div>
  )
}

const features = [
  {
    icon: "🚀",
    title: "Instant Feedback",
    description: "Real-time code analysis and suggestions help you learn faster and build better habits."
  },
  {
    icon: "🧠",
    title: "Adaptive Learning",
    description: "The curriculum evolves with you, focusing on concepts where you need the most practice."
  },
  {
    icon: "⚡",
    title: "Interactive Shell",
    description: "Run Python code directly in your browser with zero setup or installation required."
  },
]

