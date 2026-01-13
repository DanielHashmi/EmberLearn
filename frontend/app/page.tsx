'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Flame, 
  Code, 
  Brain, 
  Zap, 
  Target, 
  Trophy,
  ArrowRight,
  Sparkles,
  BookOpen,
  MessageSquare,
  BarChart3
} from 'lucide-react'
import { 
  staggerContainer, 
  staggerItem, 
  scaleIn
} from '@/src_lib/animation-presets'
import { pythonTopics } from '@/src_lib/design-tokens'
import { useAuth } from '@/src_lib/auth-context'

export default function LandingPage() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 md:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
            {/* Left Column: Text */}
            <motion.div
              className="flex-1 text-center lg:text-left z-10"
              initial="initial"
              animate="animate"
              variants={staggerContainer}
            >
              <motion.div variants={staggerItem}>
                <Badge variant="glass" className="mb-6 px-4 py-2">
                  <Sparkles className="w-4 h-4 mr-2" />
                  AI-Powered Learning Platform
                </Badge>
              </motion.div>

              <motion.h1
                variants={staggerItem}
                className="text-5xl md:text-7xl lg:text-8xl font-black mb-6 tracking-tight leading-[1.1]"
              >
                Master{' '}
                <span className="gradient-text-animated">Python</span>
                <br />
                with AI
              </motion.h1>

              <motion.p
                variants={staggerItem}
                className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-2xl leading-relaxed"
              >
                The intelligent tutoring platform that adapts to your unique
                learning style. Get personalized explanations, instant code
                reviews, and adaptive exercises.
              </motion.p>

              <motion.div
                variants={staggerItem}
                className="flex flex-wrap gap-4 justify-center lg:justify-start"
              >
                {user ? (
                  <Link href="/dashboard">
                    <Button size="xl" variant="gradient">
                      Go to Dashboard
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>
                  </Link>
                ) : (
                  <>
                    <Link href="/register">
                      <Button size="xl" variant="gradient">
                        Start Learning Free
                        <ArrowRight className="w-5 h-5 ml-2" />
                      </Button>
                    </Link>
                    <Link href="/login">
                      <Button size="xl" variant="glass">
                        Sign In
                      </Button>
                    </Link>
                  </>
                )}
              </motion.div>

              <motion.div
                variants={staggerItem}
                className="flex items-center gap-8 mt-10 justify-center lg:justify-start"
              >
                <div className="text-center">
                  <div className="text-3xl font-bold gradient-text">10K+</div>
                  <div className="text-sm text-muted-foreground">Students</div>
                </div>
                <div className="w-px h-10 bg-border" />
                <div className="text-center">
                  <div className="text-3xl font-bold gradient-text">500+</div>
                  <div className="text-sm text-muted-foreground">Exercises</div>
                </div>
                <div className="w-px h-10 bg-border" />
                <div className="text-center">
                  <div className="text-3xl font-bold gradient-text">6</div>
                  <div className="text-sm text-muted-foreground">AI Agents</div>
                </div>
              </motion.div>
            </motion.div>

            {/* Right Column: Floating Cards */}
            <div className="flex-1 w-full max-w-lg relative h-[500px] hidden lg:block">
              <FloatingCard
                title="AI Tutor"
                description="Get instant explanations"
                icon={<Brain className="w-6 h-6" />}
                className="absolute top-0 left-0 w-64"
                delay={0.2}
                rotation={-6}
              />
              <FloatingCard
                title="Code Editor"
                description="Write and run Python"
                icon={<Code className="w-6 h-6" />}
                className="absolute top-32 right-0 w-72"
                delay={0.4}
                rotation={3}
              />
              <FloatingCard
                title="Progress Tracking"
                description="See your improvement"
                icon={<BarChart3 className="w-6 h-6" />}
                className="absolute bottom-10 left-10 w-64"
                delay={0.6}
                rotation={-3}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true, margin: '-100px' }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2
              variants={staggerItem}
              className="text-4xl md:text-5xl font-bold mb-4"
            >
              Learn Smarter, Not Harder
            </motion.h2>
            <motion.p
              variants={staggerItem}
              className="text-xl text-muted-foreground max-w-2xl mx-auto"
            >
              Our AI-powered platform provides personalized learning experiences
              that adapt to your pace and style.
            </motion.p>
          </motion.div>

          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true, margin: '-100px' }}
            variants={staggerContainer}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {features.map((feature) => (
              <motion.div key={feature.title} variants={staggerItem}>
                <Card
                  variant="glass"
                  interactive
                  className="h-full hover:glow-accent transition-all duration-500"
                >
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent/20 to-accent/5 flex items-center justify-center text-accent">
                      {feature.icon}
                    </div>
                    <h3 className="text-xl font-bold">{feature.title}</h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Topics Section */}
      <section className="py-20 px-4 relative">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true, margin: '-100px' }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2
              variants={staggerItem}
              className="text-4xl md:text-5xl font-bold mb-4"
            >
              Complete Python Curriculum
            </motion.h2>
            <motion.p
              variants={staggerItem}
              className="text-xl text-muted-foreground max-w-2xl mx-auto"
            >
              From basics to advanced topics, master Python step by step with
              our structured curriculum.
            </motion.p>
          </motion.div>

          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true, margin: '-100px' }}
            variants={staggerContainer}
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
          >
            {pythonTopics.map((topic) => (
              <motion.div
                key={topic.id}
                variants={staggerItem}
                whileHover={{ scale: 1.05, y: -5 }}
                className="group"
              >
                <Card variant="glass" className="text-center p-6 h-full">
                  <div className="text-4xl mb-3">{topic.icon}</div>
                  <h3 className="font-bold mb-1">{topic.name}</h3>
                  <p className="text-xs text-muted-foreground">
                    {topic.description}
                  </p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={scaleIn}
          >
            <Card variant="glow" className="text-center p-12 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/10 to-secondary/10" />
              <div className="relative z-10">
                <motion.div
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="inline-block mb-6"
                >
                  <Flame className="w-16 h-16 text-primary" />
                </motion.div>
                <h2 className="text-4xl md:text-5xl font-bold mb-4">
                  Ready to Start Learning?
                </h2>
                <p className="text-xl text-muted-foreground mb-8 max-w-xl mx-auto">
                  Join thousands of students mastering Python with our AI-powered
                  tutoring platform.
                </p>
                <div className="flex flex-wrap gap-4 justify-center">
                  {user ? (
                    <Link href="/dashboard">
                      <Button size="xl" variant="gradient">
                        Back to Dashboard
                        <ArrowRight className="w-5 h-5 ml-2" />
                      </Button>
                    </Link>
                  ) : (
                    <>
                      <Link href="/register">
                        <Button size="xl" variant="gradient">
                          Get Started Free
                          <ArrowRight className="w-5 h-5 ml-2" />
                        </Button>
                      </Link>
                      <Link href="/login">
                        <Button size="xl" variant="outline">
                          Sign In
                        </Button>
                      </Link>
                    </>
                  )}
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t border-border/50">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Flame className="w-6 h-6 text-primary" />
              <span className="font-bold">EmberLearn</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 EmberLearn. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FloatingCard({
  title,
  description,
  icon,
  className,
  delay,
  rotation,
}: {
  title: string
  description: string
  icon: React.ReactNode
  className?: string
  delay: number
  rotation: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30, rotate: 0 }}
      animate={{ opacity: 1, y: 0, rotate: rotation }}
      transition={{ delay, duration: 0.6, type: 'spring' }}
      whileHover={{ scale: 1.05, rotate: 0, zIndex: 50 }}
      className={className}
    >
      <motion.div
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 4 + delay, repeat: Infinity, ease: 'easeInOut' }}
      >
        <Card variant="glass" className="p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent/30 to-accent/10 flex items-center justify-center text-accent">
              {icon}
            </div>
            <div>
              <h3 className="font-bold">{title}</h3>
              <p className="text-xs text-muted-foreground">{description}</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="h-2 w-full bg-muted/20 rounded-full" />
            <div className="h-2 w-3/4 bg-muted/20 rounded-full" />
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}

const features = [
  {
    icon: <Brain className="w-6 h-6" />,
    title: 'AI Explanations',
    description:
      'Get clear, personalized explanations of Python concepts adapted to your current understanding level.',
  },
  {
    icon: <Code className="w-6 h-6" />,
    title: 'Live Code Editor',
    description:
      'Write and run Python code directly in your browser with syntax highlighting and auto-completion.',
  },
  {
    icon: <MessageSquare className="w-6 h-6" />,
    title: 'Smart Debugging',
    description:
      'Our AI analyzes your errors and provides helpful hints before revealing the solution.',
  },
  {
    icon: <Target className="w-6 h-6" />,
    title: 'Adaptive Exercises',
    description:
      'Practice with exercises that automatically adjust to your skill level and learning pace.',
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: 'Progress Tracking',
    description:
      'Track your mastery across all topics with detailed analytics and streak tracking.',
  },
  {
    icon: <Trophy className="w-6 h-6" />,
    title: 'Achievements',
    description:
      'Earn badges and achievements as you progress through the curriculum and complete challenges.',
  },
]
