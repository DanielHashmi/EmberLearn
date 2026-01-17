'use client'

import { useState, useMemo, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Search, 
  Code, 
  Zap,
  Target,
  Trophy,
  CheckCircle2,
  Clock,
  ArrowRight,
  Loader2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { staggerContainer, staggerItem } from '@/src_lib/animation-presets'
import { pythonTopics } from '@/src_lib/design-tokens'
import { exercisesApi } from '@/src_lib/api'

interface Exercise {
  id: string
  title: string
  description: string
  difficulty: 'easy' | 'medium' | 'hard'
  topic: string
  topicName: string
  estimatedTime: number
  completed: boolean
  score?: number
}

export default function ExercisesPage() {
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [difficultyFilter, setDifficultyFilter] = useState('all')
  const [topicFilter, setTopicFilter] = useState('all')

  // Fetch exercises from API
  useEffect(() => {
    const fetchExercises = async () => {
      try {
        setLoading(true)
        const data = await exercisesApi.list()
        
        const mappedExercises = data.map((ex: any) => ({
          id: ex.id.toString(),
          title: ex.title,
          description: ex.description,
          difficulty: ex.difficulty,
          topic: ex.topic_slug,
          topicName: ex.topic_name,
          estimatedTime: ex.estimated_time || 15,
          completed: ex.completed || false,
          score: ex.best_score
        }))

        setExercises(mappedExercises)
      } catch (error) {
        console.error('Failed to fetch exercises:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchExercises()
  }, [])

  const filteredExercises = useMemo(() => {
    return exercises.filter(exercise => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        if (!exercise.title.toLowerCase().includes(query) && 
            !exercise.description.toLowerCase().includes(query)) {
          return false
        }
      }
      if (difficultyFilter !== 'all' && exercise.difficulty !== difficultyFilter) {
        return false
      }
      if (topicFilter !== 'all' && exercise.topic !== topicFilter) {
        return false
      }
      return true
    })
  }, [exercises, searchQuery, difficultyFilter, topicFilter])

  const stats = useMemo(() => {
    const completed = exercises.filter(e => e.completed).length
    const total = exercises.length
    return { completed, total, percentage: total > 0 ? Math.round((completed / total) * 100) : 0 }
  }, [exercises])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-24">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 md:px-8">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-xl bg-primary/20 border border-primary/30">
              <Code className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-3xl font-bold">Exercises</h1>
          </div>
          <p className="text-muted-foreground">Practice Python with hands-on coding challenges</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <Card variant="glass" className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span className="font-medium">Your Progress</span>
              </div>
              <span className="text-2xl font-bold">{stats.completed}/{stats.total}</span>
            </div>
            <Progress value={stats.percentage} size="lg" showLabel />
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-6"
        >
          <Card variant="glass" className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search exercises..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex gap-2">
                {['all', 'easy', 'medium', 'hard'].map((level) => (
                  <Button
                    key={level}
                    variant={difficultyFilter === level ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setDifficultyFilter(level)}
                  >
                    {level === 'all' ? 'All' : level.charAt(0).toUpperCase() + level.slice(1)}
                  </Button>
                ))}
              </div>
            </div>
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-border/50">
              <Button
                variant={topicFilter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTopicFilter('all')}
              >
                All Topics
              </Button>
              {pythonTopics.slice(0, 6).map((topic) => (
                <Button
                  key={topic.slug}
                  variant={topicFilter === topic.slug ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTopicFilter(topic.slug)}
                >
                  <span className="mr-1">{topic.icon}</span>
                  {topic.name}
                </Button>
              ))}
            </div>
          </Card>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-4"
        >
          {filteredExercises.length > 0 ? (
            filteredExercises.map((exercise) => (
              <motion.div key={exercise.id} variants={staggerItem}>
                <ExerciseCard exercise={exercise} />
              </motion.div>
            ))
          ) : (
            <Card variant="glass" className="p-12 text-center">
              <p className="text-muted-foreground">
                {exercises.length === 0 ? 'No exercises available yet.' : 'No exercises found.'}
              </p>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  )
}

function ExerciseCard({ exercise }: { exercise: Exercise }) {
  const difficultyConfig = {
    easy: { color: 'text-green-500', bg: 'bg-green-500/10', icon: Zap },
    medium: { color: 'text-yellow-500', bg: 'bg-yellow-500/10', icon: Target },
    hard: { color: 'text-red-500', bg: 'bg-red-500/10', icon: Trophy },
  }
  const config = difficultyConfig[exercise.difficulty]
  const DifficultyIcon = config.icon

  return (
    <Link href={`/exercise/${exercise.id}`}>
      <Card variant="glass" interactive className="p-5 hover:glow-accent transition-all">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 flex-1">
            <div className={`p-2 rounded-lg ${config.bg}`}>
              <DifficultyIcon className={`w-5 h-5 ${config.color}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-bold">{exercise.title}</h3>
                {exercise.completed && <CheckCircle2 className="w-4 h-4 text-green-500" />}
              </div>
              <p className="text-sm text-muted-foreground truncate">{exercise.description}</p>
              <div className="flex items-center gap-3 mt-2">
                <Badge variant="outline" className="text-xs">{exercise.topicName}</Badge>
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <Clock className="w-3 h-3" />{exercise.estimatedTime} min
                </span>
                {exercise.score && <span className="text-xs text-green-500">Score: {exercise.score}%</span>}
              </div>
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-muted-foreground" />
        </div>
      </Card>
    </Link>
  )
}
