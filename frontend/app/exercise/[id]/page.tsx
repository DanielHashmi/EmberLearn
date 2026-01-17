"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Play, 
  Send, 
  Loader2, 
  Terminal, 
  CheckCircle, 
  XCircle,
  ArrowLeft,
  Trophy
} from "lucide-react";
import { exercisesApi, sandboxApi } from "@/src_lib/api";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { 
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-[#1e1e1e]">
      <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
    </div>
  )
});

interface Exercise {
  id: string
  title: string
  description: string
  difficulty: string
  topic_slug: string
  topic_name: string
  starter_code: string
  solution?: string
  test_cases?: any[]
  estimated_time: number
  completed: boolean
  best_score: number
}

interface TestResult {
  passed: number
  total: number
  score: number
  details: string[]
}

export default function ExercisePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [code, setCode] = useState("");
  const [output, setOutput] = useState("");
  const [testResults, setTestResults] = useState<TestResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  useEffect(() => {
    const fetchExercise = async () => {
      try {
        setLoading(true);
        const data = await exercisesApi.getById(id);
        setExercise(data);
        setCode(data.starter_code || '# Write your solution here\n');
      } catch (error: any) {
        console.error('Failed to fetch exercise:', error);
        setFetchError(error.message || 'Failed to load exercise');
      } finally {
        setLoading(false);
      }
    }

    fetchExercise();
  }, [id]);

  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput("");
    setTestResults(null);
    
    try {
      const result = await sandboxApi.execute(code);
      if (result.success) {
        setOutput(result.output || 'Code executed successfully (no output)');
      } else {
        setOutput(`Error: ${result.error}`);
      }
    } catch (error: any) {
      setOutput(error.message || 'Connection error. Is the backend running?');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setTestResults(null);
    
    try {
      const result = await exercisesApi.submit(id, code);
      
      // Calculate passed/total from test_results array
      const testResultsArray = result.test_results || [];
      const passedCount = testResultsArray.filter((t: any) => t.passed).length;
      const totalCount = testResultsArray.length;
      
      setTestResults({
        passed: passedCount,
        total: totalCount,
        score: result.score,
        details: testResultsArray.map((t: any) => 
          `${t.passed ? '✓' : '✗'} Input: ${t.input_data} | Expected: ${t.expected} | Got: ${t.actual}`
        )
      });
      
      // Show output message
      setOutput(result.output || `Score: ${result.score}%`);
      
      // If perfect score, show success and redirect after delay
      if (result.score === 100) {
        // Update local state to show completion immediately
        if (exercise) {
          setExercise({ ...exercise, completed: true, best_score: 100 });
        }
        
        setTimeout(() => {
          router.push('/exercises');
        }, 3000);
      }
    } catch (error: any) {
      setOutput(error.message || 'Failed to submit. Is the backend running?');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-8 text-center max-w-2xl">
          <p className="text-xl font-semibold mb-4 text-red-500">Exercise not found</p>
          <p className="text-muted-foreground mb-2">Exercise ID: <code className="bg-muted px-2 py-1 rounded">{id}</code></p>
          {fetchError && (
            <div className="text-left bg-red-500/10 border border-red-500/20 rounded-lg p-4 mt-4 mb-4">
              <p className="text-sm font-semibold mb-2">Error Details:</p>
              <p className="text-sm text-muted-foreground font-mono break-all">{fetchError}</p>
            </div>
          )}
          <div className="flex gap-3 justify-center">
            <Button onClick={() => window.location.reload()} variant="outline">
              Reload Page
            </Button>
            <Button onClick={() => router.push('/exercises')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Exercises
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const difficultyColors = {
    easy: 'text-green-500 bg-green-500/10',
    medium: 'text-yellow-500 bg-yellow-500/10',
    hard: 'text-red-500 bg-red-500/10'
  };

  return (
    <div className="h-screen pt-20 pb-4 px-4">
      <div className="h-full max-w-7xl mx-auto flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => router.push('/exercises')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-bold">{exercise.title}</h1>
              <div className="flex items-center gap-2 mt-1">
                <Badge className={difficultyColors[exercise.difficulty as keyof typeof difficultyColors]}>
                  {exercise.difficulty}
                </Badge>
                <Badge variant="outline">{exercise.topic_name}</Badge>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleRunCode} disabled={isRunning} variant="outline">
              {isRunning ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Play className="w-4 h-4 mr-2" />}
              Run
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
              Submit
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
          {/* Left: Instructions & Editor */}
          <div className="flex flex-col gap-4 min-h-0">
            <Card className="p-4">
              <h2 className="font-semibold mb-2">Instructions</h2>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">{exercise.description}</p>
            </Card>
            
            <Card className="flex-1 flex flex-col overflow-hidden min-h-0">
              <div className="px-4 py-3 border-b border-border flex justify-between items-center bg-card">
                <span className="text-sm font-medium">Your Solution</span>
              </div>
              <div className="flex-1 min-h-0">
                <MonacoEditor
                  height="100%"
                  defaultLanguage="python"
                  value={code}
                  onChange={(v) => setCode(v || "")}
                  theme="vs-dark"
                  options={{ 
                    minimap: { enabled: false }, 
                    fontSize: 14, 
                    padding: { top: 16 },
                    scrollBeyondLastLine: false
                  }}
                />
              </div>
            </Card>
          </div>

          {/* Right: Output & Results */}
          <div className="flex flex-col gap-4 min-h-0">
            {/* Test Results */}
            {testResults && (
              <Card className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-semibold">Test Results</h2>
                  <div className="flex items-center gap-2">
                    {testResults.score === 100 ? (
                      <Trophy className="w-5 h-5 text-yellow-500" />
                    ) : null}
                    <span className="text-2xl font-bold">{testResults.score}%</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Tests Passed</span>
                    <span className="font-medium">{testResults.passed}/{testResults.total}</span>
                  </div>
                  {testResults.score === 100 && (
                    <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3 text-sm text-green-500">
                      <CheckCircle className="w-4 h-4 inline mr-2" />
                      Perfect! Redirecting to exercises...
                    </div>
                  )}
                  {testResults.score < 100 && testResults.score > 0 && (
                    <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-500">
                      Good progress! Keep trying to pass all tests.
                    </div>
                  )}
                  {testResults.score === 0 && (
                    <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-sm text-red-500">
                      <XCircle className="w-4 h-4 inline mr-2" />
                      No tests passed. Review the instructions and try again.
                    </div>
                  )}
                </div>
              </Card>
            )}

            {/* Output Console */}
            <Card className="flex-1 flex flex-col min-h-0">
              <div className="px-4 py-2 border-b border-border flex items-center gap-2 bg-card">
                <Terminal size={14} />
                <span className="text-xs font-medium uppercase">Output</span>
              </div>
              <div className="flex-1 p-3 overflow-auto bg-[#0d1117] font-mono text-sm">
                <pre className="text-green-400">{output || "Click Run to test your code..."}</pre>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
