'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  Flame, 
  Trophy, 
  Target, 
  Zap, 
  BookOpen, 
  Code, 
  Play,
  ChevronRight
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress, ProgressRing } from '@/components/ui/progress'
import { GlowBackground } from '@/components/shared/glow-background'
import { 
  staggerContainer, 
  staggerItem
} from '@/src_lib/animation-presets'
import { pythonTopics, getMasteryLevel, getMasteryColor } from '@/src_lib/design-tokens'
import { useAuth } from '@/src_lib/auth-context'
import { progressApi } from '@/src_lib/api'

export default function DashboardPage() {
  const [isLoaded, setIsLoaded] = useState(false)
  const { user, isLoading } = useAuth()
  const router = useRouter()
  
  // User progress state
  const [userProgress, setUserProgress] = useState({
    streak: 0,
    totalXP: 0,
    level: 1,
    completedExercises: 0,
    overallProgress: 0,
    topics: [] as any[]
  })
  const [loadingProgress, setLoadingProgress] = useState(true)

  useEffect(() => {
    setIsLoaded(true)
  }, [])

  // Fetch real progress from API
  useEffect(() => {
    const fetchProgress = async () => {
      if (!user) return
      
      try {
        setLoadingProgress(true)
        const data = await progressApi.getStats()
        
        setUserProgress({
          streak: data.streak || 0,
          totalXP: data.total_xp || 0,
          level: data.level || 1,
          completedExercises: data.topics?.reduce((sum: number, t: any) => sum + t.exercises_completed, 0) || 0,
          overallProgress: Math.round(data.overall_mastery || 0),
          topics: data.topics || []
        })
      } catch (error) {
        console.error('Failed to fetch progress:', error)
      } finally {
        setLoadingProgress(false)
      }
    }
    
    fetchProgress()
  }, [user])

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login')
    }
  }, [user, isLoading, router])

  const userName = user?.name?.split(' ')[0] || 'Learner'

  // Map API topics to display format
  const topicProgress = userProgress.topics.length > 0 
    ? userProgress.topics.map((apiTopic: any) => {
        const designTopic = pythonTopics.find(t => t.name.toLowerCase().includes(apiTopic.name.toLowerCase()))
        return {
          id: apiTopic.slug,
          name: apiTopic.name,
          slug: apiTopic.slug,
          icon: designTopic?.icon || '📚',
          description: designTopic?.description || '',
          masteryScore: Math.round(apiTopic.mastery_score || 0),
          exercisesCompleted: apiTopic.exercises_completed || 0,
          totalExercises: apiTopic.total_exercises || 0
        }
      })
    : pythonTopics.map((topic, index) => ({
        ...topic,
        masteryScore: 0,
        exercisesCompleted: 0,
        totalExercises: 15
      }))

  if (isLoading || loadingProgress) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen relative pt-24 pb-12 px-4 md:px-8">
      <GlowBackground />
      
      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial="initial"
          animate={isLoaded ? "animate" : "initial"}
          variants={staggerContainer}
          className="mb-8"
        >
          <motion.div variants={staggerItem} className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold mb-2">
                Welcome back, <span className="gradient-text">{userName}</span>
              </h1>
              <p className="text-muted-foreground text-lg">
                Continue your Python journey. You're doing great!
              </p>
            </div>
            <Link href="/practice/basics">
              <Button size="lg" variant="gradient">
                <Play className="w-5 h-5 mr-2" />
                Continue Learning
              </Button>
            </Link>
          </motion.div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial="initial"
          animate={isLoaded ? "animate" : "initial"}
          variants={staggerContainer}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          <StatCard
            icon={<Flame className="w-6 h-6 text-orange-500" />}
            label="Day Streak"
            value={userProgress.streak}
            suffix="days"
          />
          <StatCard
            icon={<Zap className="w-6 h-6 text-yellow-500" />}
            label="Total XP"
            value={userProgress.totalXP.toLocaleString()}
          />
          <StatCard
            icon={<Trophy className="w-6 h-6 text-purple-500" />}
            label="Level"
            value={userProgress.level}
          />
          <StatCard
            icon={<Target className="w-6 h-6 text-green-500" />}
            label="Exercises"
            value={`${userProgress.completedExercises}/120`}
          />
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content - Topics */}
          <div className="lg:col-span-2 space-y-6">
            {/* Overall Progress */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={isLoaded ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.2 }}
            >
              <Card variant="glass" className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">Overall Progress</h2>
                  <Badge variant="glass">{userProgress.overallProgress}% Complete</Badge>
                </div>
                <Progress 
                  value={userProgress.overallProgress} 
                  showLabel 
                  size="lg"
                  className="mb-2"
                />
                <p className="text-sm text-muted-foreground">
                  Keep going! You're making excellent progress.
                </p>
              </Card>
            </motion.div>

            {/* Topics Grid */}
            <motion.div
              initial="initial"
              animate={isLoaded ? "animate" : "initial"}
              variants={staggerContainer}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">Your Topics</h2>
                <Link href="/exercises" className="text-sm text-primary hover:underline flex items-center">
                  View all <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
              
              <div className="grid sm:grid-cols-2 gap-4">
                {topicProgress.map((topic) => (
                  <motion.div key={topic.id} variants={staggerItem}>
                    <TopicCard topic={topic} />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={isLoaded ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: 0.3 }}
            >
              <Card variant="glass" className="p-6">
                <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
                <div className="space-y-3">
                  <Link href="/chat" className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <BookOpen className="w-4 h-4 mr-2" />
                      Ask AI Tutor
                    </Button>
                  </Link>
                  <Link href="/practice/basics" className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <Code className="w-4 h-4 mr-2" />
                      Practice Coding
                    </Button>
                  </Link>
                  <Link href="/exercises" className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <Target className="w-4 h-4 mr-2" />
                      Browse Exercises
                    </Button>
                  </Link>
                </div>
              </Card>
            </motion.div>

            {/* Learning Tips */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={isLoaded ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: 0.4 }}
            >
              <Card variant="glow" className="p-6">
                <h2 className="text-xl font-bold mb-4">💡 Learning Tip</h2>
                <p className="text-muted-foreground text-sm">
                  Practice coding every day, even if it's just for 15 minutes. 
                  Consistency is key to mastering Python!
                </p>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ 
  icon, 
  label, 
  value, 
  suffix
}: { 
  icon: React.ReactNode
  label: string
  value: string | number
  suffix?: string
}) {
  return (
    <motion.div variants={staggerItem}>
      <Card variant="glass" className="p-4 h-full">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
            {icon}
          </div>
          <div>
            <p className="text-2xl font-bold">
              {value}
              {suffix && <span className="text-sm font-normal text-muted-foreground ml-1">{suffix}</span>}
            </p>
            <p className="text-sm text-muted-foreground">{label}</p>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

function TopicCard({ topic }: { topic: { 
  id: string
  name: string
  slug: string
  icon: string
  description: string
  masteryScore: number
  exercisesCompleted: number
  totalExercises: number
}}) {
  const masteryLevel = getMasteryLevel(topic.masteryScore)
  const masteryColor = getMasteryColor(topic.masteryScore)

  return (
    <Link href={`/practice/${topic.slug}`}>
      <Card 
        variant="glass" 
        interactive 
        className="p-5 h-full hover:glow-accent transition-all duration-300"
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{topic.icon}</span>
            <div>
              <h3 className="font-bold">{topic.name}</h3>
              <p className="text-xs text-muted-foreground">{topic.description}</p>
            </div>
          </div>
          <ProgressRing 
            value={topic.masteryScore} 
            size={48} 
            strokeWidth={4}
          />
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Mastery</span>
            <Badge 
              variant="outline" 
              className="text-xs"
              style={{ borderColor: masteryColor, color: masteryColor }}
            >
              {masteryLevel.label}
            </Badge>
          </div>
          <Progress value={topic.masteryScore} size="sm" />
          <p className="text-xs text-muted-foreground">
            {topic.exercisesCompleted}/{topic.totalExercises} exercises completed
          </p>
        </div>
      </Card>
    </Link>
  )
}
