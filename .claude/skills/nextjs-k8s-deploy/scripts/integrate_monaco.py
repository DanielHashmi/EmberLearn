#!/usr/bin/env python3
"""Integrate Monaco Editor into Next.js with SSR-safe dynamic import."""

import argparse
from pathlib import Path


CODE_EDITOR_COMPONENT = '''\'use client\'

import dynamic from 'next/dynamic'
import { useState, useCallback } from 'react'

// Dynamic import with SSR disabled for Monaco Editor
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full bg-gray-100">
        <div className="animate-pulse text-gray-500">Loading editor...</div>
      </div>
    )
  }
)

interface CodeEditorProps {
  initialCode?: string
  onCodeChange?: (code: string) => void
  onRunCode?: (code: string) => void
}

export default function CodeEditor({
  initialCode = '# Write your Python code here\\nprint("Hello, EmberLearn!")',
  onCodeChange,
  onRunCode
}: CodeEditorProps) {
  const [code, setCode] = useState(initialCode)
  const [output, setOutput] = useState<string>('')
  const [isRunning, setIsRunning] = useState(false)

  const handleEditorChange = useCallback((value: string | undefined) => {
    const newCode = value || ''
    setCode(newCode)
    onCodeChange?.(newCode)
  }, [onCodeChange])

  const handleRunCode = useCallback(async () => {
    setIsRunning(true)
    setOutput('Running...')

    try {
      const response = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      })

      const result = await response.json()
      setOutput(result.output || result.error || 'No output')
      onRunCode?.(code)
    } catch (error) {
      setOutput(`Error: ${error}`)
    } finally {
      setIsRunning(false)
    }
  }, [code, onRunCode])

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Editor toolbar */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500">Python Editor</span>
        <button
          onClick={handleRunCode}
          disabled={isRunning}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRunning ? 'Running...' : '▶ Run Code'}
        </button>
      </div>

      {/* Monaco Editor */}
      <div className="monaco-container flex-1">
        <MonacoEditor
          height="100%"
          language="python"
          theme="vs-light"
          value={code}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
          }}
        />
      </div>

      {/* Output panel */}
      <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-32 overflow-auto">
        <div className="text-gray-500 text-xs mb-2">Output:</div>
        <pre className="whitespace-pre-wrap">{output || 'Run your code to see output'}</pre>
      </div>
    </div>
  )
}
'''


CHAT_PANEL_COMPONENT = '''\'use client\'

import { useState, useCallback, useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'Sorry, I could not process your request.',
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
    } finally {
      setIsLoading(false)
    }
  }, [input, isLoading])

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="font-semibold text-gray-800">AI Tutor</h2>
        <p className="text-xs text-gray-500">Ask questions about Python</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p>👋 Hi! I\\'m your Python tutor.</p>
            <p className="text-sm mt-2">Ask me anything about Python!</p>
          </div>
        )}

        {messages.map(message => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about Python..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
'''


PROGRESS_DASHBOARD_COMPONENT = '''\'use client\'

import { useEffect, useState } from 'react'
import useSWR from 'swr'

interface TopicProgress {
  id: string
  name: string
  mastery: number
  exercisesCompleted: number
  totalExercises: number
}

const fetcher = (url: string) => fetch(url).then(res => res.json())

function getMasteryClass(mastery: number): string {
  if (mastery < 0.4) return 'mastery-red'
  if (mastery < 0.7) return 'mastery-yellow'
  if (mastery < 0.9) return 'mastery-green'
  return 'mastery-blue'
}

function getMasteryLabel(mastery: number): string {
  if (mastery < 0.4) return 'Needs Practice'
  if (mastery < 0.7) return 'Developing'
  if (mastery < 0.9) return 'Proficient'
  return 'Mastered'
}

export default function ProgressDashboard() {
  const { data: topics, error } = useSWR<TopicProgress[]>('/api/progress', fetcher)

  if (error) {
    return <div className="text-red-500 text-sm">Failed to load progress</div>
  }

  if (!topics) {
    return <div className="animate-pulse text-gray-400">Loading...</div>
  }

  const overallMastery = topics.length > 0
    ? topics.reduce((sum, t) => sum + t.mastery, 0) / topics.length
    : 0

  return (
    <div className="space-y-4">
      <div>
        <h2 className="font-semibold text-gray-800">Your Progress</h2>
        <div className="mt-2 p-3 bg-gray-100 rounded-lg">
          <div className="text-2xl font-bold text-gray-800">
            {Math.round(overallMastery * 100)}%
          </div>
          <div className="text-xs text-gray-500">Overall Mastery</div>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-600 mb-2">Topics</h3>
        <div className="space-y-2">
          {topics.map(topic => (
            <div
              key={topic.id}
              className={`p-2 rounded border ${getMasteryClass(topic.mastery)}`}
            >
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">{topic.name}</span>
                <span className="text-xs">{Math.round(topic.mastery * 100)}%</span>
              </div>
              <div className="mt-1 h-1.5 bg-white/50 rounded-full overflow-hidden">
                <div
                  className="h-full bg-current opacity-60 transition-all"
                  style={{ width: `${topic.mastery * 100}%` }}
                />
              </div>
              <div className="text-xs mt-1 opacity-75">
                {getMasteryLabel(topic.mastery)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
'''


def integrate_monaco(project_dir: Path) -> None:
    """Create Monaco Editor integration components."""
    components_dir = project_dir / "app" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    # Write CodeEditor component
    (components_dir / "CodeEditor.tsx").write_text(CODE_EDITOR_COMPONENT)
    print(f"✓ Created {components_dir}/CodeEditor.tsx")

    # Write ChatPanel component
    (components_dir / "ChatPanel.tsx").write_text(CHAT_PANEL_COMPONENT)
    print(f"✓ Created {components_dir}/ChatPanel.tsx")

    # Write ProgressDashboard component
    (components_dir / "ProgressDashboard.tsx").write_text(PROGRESS_DASHBOARD_COMPONENT)
    print(f"✓ Created {components_dir}/ProgressDashboard.tsx")

    print(f"\n✓ Monaco Editor integration complete!")


def main():
    parser = argparse.ArgumentParser(description="Integrate Monaco Editor into Next.js")
    parser.add_argument("project_dir", type=Path, help="Path to Next.js project")
    args = parser.parse_args()

    if not args.project_dir.exists():
        print(f"✗ Directory not found: {args.project_dir}")
        return

    integrate_monaco(args.project_dir)


if __name__ == "__main__":
    main()
