'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle2, XCircle, Clock, Loader2, Eye, EyeOff } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/src_lib/utils'
import { useState } from 'react'

export interface TestCase {
  id: string
  name: string
  input: string
  expectedOutput: string
  actualOutput?: string
  passed?: boolean
  hidden?: boolean
  executionTime?: number
}

export interface TestResultsProps {
  testCases: TestCase[]
  isRunning?: boolean
  totalScore?: number
  executionTime?: number
}

export function TestResults({ testCases, isRunning, totalScore, executionTime }: TestResultsProps) {
  const [showHidden, setShowHidden] = useState(false)
  
  const passedCount = testCases.filter(tc => tc.passed).length
  const visibleTests = testCases.filter(tc => !tc.hidden || showHidden)
  const hiddenCount = testCases.filter(tc => tc.hidden).length

  return (
    <div className="space-y-4">
      {/* Summary Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-white">Test Results</h3>
          {!isRunning && testCases.some(tc => tc.passed !== undefined) && (
            <Badge 
              className={cn(
                'text-sm',
                passedCount === testCases.length 
                  ? 'bg-green-500/20 text-green-400 border-green-500/30'
                  : 'bg-red-500/20 text-red-400 border-red-500/30'
              )}
            >
              {passedCount}/{testCases.length} Passed
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-3">
          {executionTime !== undefined && (
            <span className="text-xs text-white/50 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {executionTime}ms
            </span>
          )}
          {hiddenCount > 0 && (
            <button
              onClick={() => setShowHidden(!showHidden)}
              className="text-xs text-white/50 hover:text-white/80 flex items-center gap-1 transition-colors"
            >
              {showHidden ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              {showHidden ? 'Hide' : 'Show'} hidden ({hiddenCount})
            </button>
          )}
        </div>
      </div>

      {/* Loading State */}
      {isRunning && (
        <Card className="border-white/10 bg-white/5 backdrop-blur-xl p-6">
          <div className="flex items-center justify-center gap-3">
            <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
            <span className="text-white/70">Running tests...</span>
          </div>
        </Card>
      )}

      {/* Test Cases */}
      <AnimatePresence mode="popLayout">
        {!isRunning && visibleTests.map((testCase, index) => (
          <motion.div
            key={testCase.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ delay: index * 0.05 }}
          >
            <Card className={cn(
              'border-white/10 bg-white/5 backdrop-blur-xl overflow-hidden',
              testCase.passed === true && 'border-green-500/30',
              testCase.passed === false && 'border-red-500/30'
            )}>
              <div className="p-4">
                {/* Test Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {testCase.passed === undefined ? (
                      <div className="w-5 h-5 rounded-full border-2 border-white/30" />
                    ) : testCase.passed ? (
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-400" />
                    )}
                    <span className="font-medium text-white">{testCase.name}</span>
                    {testCase.hidden && (
                      <Badge variant="outline" className="text-xs text-white/40 border-white/20">
                        Hidden
                      </Badge>
                    )}
                  </div>
                  {testCase.executionTime !== undefined && (
                    <span className="text-xs text-white/40">{testCase.executionTime}ms</span>
                  )}
                </div>

                {/* Test Details */}
                <div className="space-y-2 text-sm">
                  <div className="grid grid-cols-[80px_1fr] gap-2">
                    <span className="text-white/50">Input:</span>
                    <code className="bg-black/30 px-2 py-1 rounded text-white/80 font-mono text-xs">
                      {testCase.input}
                    </code>
                  </div>
                  <div className="grid grid-cols-[80px_1fr] gap-2">
                    <span className="text-white/50">Expected:</span>
                    <code className="bg-black/30 px-2 py-1 rounded text-green-400/80 font-mono text-xs">
                      {testCase.expectedOutput}
                    </code>
                  </div>
                  {testCase.actualOutput !== undefined && (
                    <div className="grid grid-cols-[80px_1fr] gap-2">
                      <span className="text-white/50">Actual:</span>
                      <code className={cn(
                        'bg-black/30 px-2 py-1 rounded font-mono text-xs',
                        testCase.passed ? 'text-green-400/80' : 'text-red-400/80'
                      )}>
                        {testCase.actualOutput}
                      </code>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Score Summary */}
      {totalScore !== undefined && !isRunning && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Card className={cn(
            'border-white/10 bg-gradient-to-r p-6 text-center',
            totalScore === 100 
              ? 'from-green-500/20 to-emerald-500/20 border-green-500/30'
              : totalScore >= 50
              ? 'from-yellow-500/20 to-orange-500/20 border-yellow-500/30'
              : 'from-red-500/20 to-pink-500/20 border-red-500/30'
          )}>
            <div className="text-4xl font-bold text-white mb-1">{totalScore}%</div>
            <div className="text-sm text-white/60">
              {totalScore === 100 ? 'Perfect Score!' : totalScore >= 50 ? 'Good Progress!' : 'Keep Trying!'}
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  )
}
