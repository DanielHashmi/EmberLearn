'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Clock, CheckCircle2, Circle, ChevronRight, Zap, Target, Trophy } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/src_lib/utils'

export interface Exercise {
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

interface ExerciseCardProps {
  exercise: Exercise
  index?: number
}

const difficultyConfig = {
  easy: {
    label: 'Easy',
    color: 'bg-green-500/20 text-green-400 border-green-500/30',
    icon: Zap,
  },
  medium: {
    label: 'Medium',
    color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    icon: Target,
  },
  hard: {
    label: 'Hard',
    color: 'bg-red-500/20 text-red-400 border-red-500/30',
    icon: Trophy,
  },
}

export function ExerciseCard({ exercise, index = 0 }: ExerciseCardProps) {
  const difficulty = difficultyConfig[exercise.difficulty]
  const DifficultyIcon = difficulty.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
    >
      <Link href={`/exercises/${exercise.id}`}>
        <Card className="group relative overflow-hidden border-white/10 bg-white/5 backdrop-blur-xl hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 cursor-pointer">
          {/* Glow effect on hover */}
          <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-transparent to-blue-500/10" />
          </div>

          <div className="relative p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                {/* Header with status and difficulty */}
                <div className="flex items-center gap-2 mb-2">
                  {exercise.completed ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                  ) : (
                    <Circle className="w-5 h-5 text-white/30 flex-shrink-0" />
                  )}
                  <Badge className={cn('text-xs', difficulty.color)}>
                    <DifficultyIcon className="w-3 h-3 mr-1" />
                    {difficulty.label}
                  </Badge>
                  <Badge variant="outline" className="text-xs text-white/60 border-white/20">
                    {exercise.topicName}
                  </Badge>
                </div>

                {/* Title */}
                <h3 className="text-lg font-semibold text-white group-hover:text-purple-300 transition-colors truncate">
                  {exercise.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-white/60 mt-1 line-clamp-2">
                  {exercise.description}
                </p>

                {/* Footer with time and score */}
                <div className="flex items-center gap-4 mt-3 text-xs text-white/50">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {exercise.estimatedTime} min
                  </span>
                  {exercise.completed && exercise.score !== undefined && (
                    <span className="flex items-center gap-1 text-green-400">
                      <Trophy className="w-3.5 h-3.5" />
                      {exercise.score}%
                    </span>
                  )}
                </div>
              </div>

              {/* Arrow indicator */}
              <ChevronRight className="w-5 h-5 text-white/30 group-hover:text-purple-400 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
            </div>
          </div>
        </Card>
      </Link>
    </motion.div>
  )
}
