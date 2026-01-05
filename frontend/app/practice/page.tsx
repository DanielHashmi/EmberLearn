"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getUser, logout } from "@/lib/auth";
import { api } from "@/lib/api";
import CodeEditor from "@/components/CodeEditor";
import OutputPanel from "@/components/OutputPanel";

export default function PracticePage() {
  const router = useRouter();
  const [user, setUser] = useState<{ id: string; name: string } | null>(null);
  const [code, setCode] = useState("# Write your Python code here\nprint('Hello, EmberLearn!')\n");
  const [output, setOutput] = useState("");
  const [error, setError] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [executionTime, setExecutionTime] = useState<number | undefined>();
  const [question, setQuestion] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [isAsking, setIsAsking] = useState(false);

  useEffect(() => {
    const currentUser = getUser();
    if (!currentUser) {
      router.push("/login");
      return;
    }
    setUser(currentUser);
  }, [router]);

  const handleRunCode = useCallback(
    async (codeToRun: string) => {
      if (!user) return;

      setIsRunning(true);
      setOutput("");
      setError("");
      setExecutionTime(undefined);

      try {
        const result = await api.executeCode({
          code: codeToRun,
          student_id: user.id,
          timeout_ms: 5000,
        });

        setOutput(result.output);
        if (result.error) {
          setError(result.error);
        }
        setExecutionTime(result.execution_time_ms);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Execution failed");
      } finally {
        setIsRunning(false);
      }
    },
    [user]
  );

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !question.trim()) return;

    setIsAsking(true);
    setAiResponse("");

    try {
      const result = await api.query({
        query: question,
        student_id: user.id,
        context: { code },
      });
      setAiResponse(result.response);
    } catch (err) {
      setAiResponse(`Error: ${err instanceof Error ? err.message : "Failed to get response"}`);
    } finally {
      setIsAsking(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-bold text-blue-600">
            EmberLearn
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/exercises/variables" className="text-gray-600 hover:text-gray-900">
              Exercises
            </Link>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">{user?.name}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Sign Out
              </button>
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 py-6 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-180px)]">
          {/* Left: Code Editor */}
          <div className="flex flex-col gap-4">
            <div className="flex-1 min-h-0">
              <CodeEditor
                initialCode={code}
                onChange={setCode}
                onRun={handleRunCode}
                height="100%"
              />
            </div>
            <div className="h-48">
              <OutputPanel
                output={output}
                error={error}
                isLoading={isRunning}
                executionTime={executionTime}
              />
            </div>
          </div>

          {/* Right: AI Chat */}
          <div className="bg-white rounded-xl border flex flex-col">
            <div className="px-4 py-3 border-b">
              <h2 className="font-semibold text-gray-900">AI Tutor</h2>
              <p className="text-sm text-gray-500">Ask questions about Python or your code</p>
            </div>

            <div className="flex-1 p-4 overflow-auto">
              {aiResponse ? (
                <div className="prose prose-sm max-w-none">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <p className="whitespace-pre-wrap">{aiResponse}</p>
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400">
                  <p>Ask a question to get started</p>
                </div>
              )}
            </div>

            <form onSubmit={handleAskQuestion} className="p-4 border-t">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="How do I use a for loop?"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  type="submit"
                  disabled={isAsking || !question.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {isAsking ? "..." : "Ask"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
