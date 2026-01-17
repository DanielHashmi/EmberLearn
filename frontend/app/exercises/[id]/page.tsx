'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, 
  Play, 
  RotateCcw, 
  Lightbulb, 
  CheckCircle2,
  Clock,
  Zap,
  Target,
  Trophy,
  Send
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TestResults, TestCase } from '@/components/exercises/test-results'
import { cn } from '@/src_lib/utils'
import { exercisesApi } from '@/src_lib/api'

// Dynamic import for Monaco Editor (SSR-safe)
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react').then(mod => mod.default),
  { 
    ssr: false,
    loading: () => (
      <div className="h-full flex items-center justify-center bg-slate-900/50 rounded-lg">
        <div className="text-white/50">Loading editor...</div>
      </div>
    )
  }
)

// Mock exercise data as fallback
const mockExerciseDetails: Record<string, any> = {
  '1': {
    id: '1',
    title: 'Hello World',
    description: 'Write your first Python program that prints "Hello, World!"',
    difficulty: 'easy',
    topic: 'basics',
    topicName: 'Basics',
    estimatedTime: 5,
    instructions: `Write a Python program that prints the text "Hello, World!" to the console.`,
    starterCode: '# Write your code here\n',
    hints: ['Use the print() function'],
    testCases: [],
  }
}

const difficultyConfig = {
  easy: { label: 'Easy', color: 'bg-green-500/20 text-green-400 border-green-500/30', icon: Zap },
  medium: { label: 'Medium', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30', icon: Target },
  hard: { label: 'Hard', color: 'bg-red-500/20 text-red-400 border-red-500/30', icon: Trophy },
}

export default function ExerciseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const exerciseId = params.id as string
  
  const [code, setCode] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [testResults, setTestResults] = useState<TestCase[]>([])
  const [showHints, setShowHints] = useState(false)
  const [currentHint, setCurrentHint] = useState(0)
  const [totalScore, setTotalScore] = useState<number | undefined>()
  const [exercise, setExercise] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  // Fetch exercise from API
  useEffect(() => {
    const fetchExercise = async () => {
      try {
        setLoading(true)
        const data = await exercisesApi.getById(exerciseId)
        
        setExercise({
          id: data.id.toString(),
          title: data.title,
          description: data.description,
          difficulty: data.difficulty,
          topic: data.topic_slug,
          topicName: data.topic_name,
          estimatedTime: data.estimated_time || 15,
          instructions: data.description,
          starterCode: data.starter_code || '# Write your code here\n',
          hints: ['Use the print() function', 'Check your syntax', 'Test with different inputs'],
          testCases: []
        })
        setCode(data.starter_code || '# Write your code here\n')
      } catch (error) {
        console.error('Failed to fetch exercise:', error)
        // Fallback to mock data
        const mockEx = mockExerciseDetails[exerciseId] || mockExerciseDetails['1']
        setExercise(mockEx)
        setCode(mockEx.starterCode)
      } finally {
        setLoading(false)
      }
    }
    
    fetchExercise()
  }, [exerciseId])

  const handleRun = async () => {
    if (!exercise) return
    
    setIsRunning(true)
    setTotalScore(undefined)
    
    try {
      const result = await exercisesApi.submit(exerciseId, code)
      
      // Map API response to test results
      const results = result.test_results.map((tr: any, index: number) => ({
        id: index.toString(),
        name: tr.test_name || `Test ${index + 1}`,
        input: tr.input_data,
        expectedOutput: tr.expected,
        passed: tr.passed,
        actualOutput: tr.actual,
        executionTime: 0
      }))
      
      setTestResults(results)
      setTotalScore(result.score)
      
      if (result.score === 100) {
        // Show success and maybe redirect after delay
        setTimeout(() => {
          router.push('/exercises')
        }, 3000)
      }
    } catch (error) {
      console.error('Submission error:', error)
    } finally {
      setIsRunning(false)
    }
  }

  const handleReset = () => {
    if (exercise) {
      setCode(exercise.starterCode)
      setTestResults([])
      setTotalScore(undefined)
    }
  }

  if (loading || !exercise) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white">Loading exercise...</div>
      </div>
    )
  }

  const difficulty = difficultyConfig[exercise.difficulty]
  const DifficultyIcon = difficulty.icon

  const handleNextHint = () => {
    if (currentHint < exercise.hints.length - 1) {
      setCurrentHint(prev => prev + 1)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950/20 to-slate-950">
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/exercises')}
            className="text-white/60 hover:text-white mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Exercises
          </Button>

          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge className={cn('text-xs', difficulty.color)}>
                  <DifficultyIcon className="w-3 h-3 mr-1" />
                  {difficulty.label}
                </Badge>
                <Badge variant="outline" className="text-xs text-white/60 border-white/20">
                  {exercise.topicName}
                </Badge>
                <span className="text-xs text-white/40 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  ~{exercise.estimatedTime} min
                </span>
              </div>
              <h1 className="text-2xl font-bold text-white">{exercise.title}</h1>
              <p className="text-white/60 mt-1">{exercise.description}</p>
            </div>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Instructions & Hints */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="space-y-4"
          >
            {/* Instructions */}
            <Card className="border-white/10 bg-white/5 backdrop-blur-xl p-5">
              <h2 className="text-lg font-semibold text-white mb-3">Instructions</h2>
              <div className="text-white/70 whitespace-pre-wrap text-sm leading-relaxed">
                {exercise.instructions}
              </div>
            </Card>

            {/* Hints */}
            <Card className="border-white/10 bg-white/5 backdrop-blur-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  Hints
                </h2>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowHints(!showHints)}
                  className="bg-transparent border-white/10 text-white/60 hover:bg-white/5"
                >
                  {showHints ? 'Hide' : 'Show'} Hints
                </Button>
              </div>

              {showHints && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="space-y-2"
                >
                  {exercise.hints.slice(0, currentHint + 1).map((hint, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-sm text-yellow-200/80"
                    >
                      <span className="font-medium text-yellow-400">Hint {index + 1}:</span> {hint}
                    </motion.div>
                  ))}
                  {currentHint < exercise.hints.length - 1 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleNextHint}
                      className="w-full bg-transparent border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10"
                    >
                      Show Next Hint ({currentHint + 1}/{exercise.hints.length})
                    </Button>
                  )}
                </motion.div>
              )}
            </Card>

            {/* Test Results */}
            <TestResults 
              testCases={testResults} 
              isRunning={isRunning}
              totalScore={totalScore}
            />
          </motion.div>

          {/* Right Panel - Code Editor */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-4"
          >
            <Card className="border-white/10 bg-white/5 backdrop-blur-xl overflow-hidden">
              {/* Editor Toolbar */}
              <div className="flex items-center justify-between p-3 border-b border-white/10 bg-white/5">
                <span className="text-sm text-white/60">solution.py</span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleReset}
                    className="bg-transparent border-white/10 text-white/60 hover:bg-white/5"
                  >
                    <RotateCcw className="w-4 h-4 mr-1" />
                    Reset
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleRun}
                    disabled={isRunning}
                    className="bg-green-500/20 text-green-400 border-green-500/30 hover:bg-green-500/30"
                  >
                    <Play className="w-4 h-4 mr-1" />
                    {isRunning ? 'Running...' : 'Run Tests'}
                  </Button>
                </div>
              </div>

              {/* Monaco Editor */}
              <div className="h-[500px]">
                <MonacoEditor
                  height="100%"
                  language="python"
                  theme="vs-dark"
                  value={code}
                  onChange={(value) => setCode(value || '')}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    tabSize: 4,
                    wordWrap: 'on',
                    padding: { top: 16, bottom: 16 },
                  }}
                />
              </div>
            </Card>

            {/* Submit Button */}
            <Button
              size="lg"
              onClick={handleRun}
              disabled={isRunning || totalScore === 100}
              className={cn(
                'w-full',
                totalScore === 100
                  ? 'bg-green-500/20 text-green-400 border-green-500/30'
                  : 'bg-purple-500/20 text-purple-300 border-purple-500/30 hover:bg-purple-500/30'
              )}
            >
              {totalScore === 100 ? (
                <>
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  Exercise Completed!
                </>
              ) : (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Submit Solution
                </>
              )}
            </Button>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
