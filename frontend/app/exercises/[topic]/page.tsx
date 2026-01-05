"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { getUser, logout } from "@/lib/auth";
import { api } from "@/lib/api";
import { TOPICS, type Exercise } from "@/lib/types";
import CodeEditor from "@/components/CodeEditor";
import OutputPanel from "@/components/OutputPanel";
import ExerciseCard from "@/components/ExerciseCard";

export default function ExerciseTopicPage() {
  const router = useRouter();
  const params = useParams();
  const topicId = params.topic as string;

  const [user, setUser] = useState<{ id: string; name: string } | null>(null);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [activeExercise, setActiveExercise] = useState<Exercise | null>(null);
  const [code, setCode] = useState("");
  const [output, setOutput] = useState("");
  const [error, setError] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(true);

  const topic = TOPICS.find((t) => t.id === topicId);

  useEffect(() => {
    const currentUser = getUser();
    if (!currentUser) {
      router.push("/login");
      return;
    }
    setUser(currentUser);

    // Generate initial exercise for this topic
    api
      .generateExercise({
        topic: topicId,
        difficulty: "beginner",
        student_id: currentUser.id,
      })
      .then((exercise) => {
        setExercises([exercise]);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [router, topicId]);

  const handleStartExercise = (exercise: Exercise) => {
    setActiveExercise(exercise);
    setCode(exercise.starter_code);
    setOutput("");
    setError("");
    setFeedback("");
  };

  const handleRunCode = useCallback(
    async (codeToRun: string) => {
      if (!user) return;

      setIsRunning(true);
      setOutput("");
      setError("");

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
      } catch (err) {
        setError(err instanceof Error ? err.message : "Execution failed");
      } finally {
        setIsRunning(false);
      }
    },
    [user]
  );

  const handleSubmit = async () => {
    if (!user || !activeExercise) return;

    setIsSubmitting(true);
    setFeedback("");

    try {
      const result = await api.submitExercise({
        exercise_id: activeExercise.id,
        code,
        student_id: user.id,
      });

      if (result.passed) {
        setFeedback(`✅ All tests passed! Score: ${result.score}/100\n\n${result.feedback}`);
      } else {
        const failedTests = result.test_results.filter((t) => !t.passed);
        setFeedback(
          `❌ ${failedTests.length} test(s) failed.\n\n${result.feedback}\n\nKeep trying!`
        );
      }
    } catch (err) {
      setFeedback(`Error: ${err instanceof Error ? err.message : "Submission failed"}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGenerateNew = async (difficulty: "beginner" | "intermediate" | "advanced") => {
    if (!user) return;

    setLoading(true);
    try {
      const exercise = await api.generateExercise({
        topic: topicId,
        difficulty,
        student_id: user.id,
      });
      setExercises((prev) => [...prev, exercise]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
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
            <Link href="/practice" className="text-gray-600 hover:text-gray-900">
              Practice
            </Link>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">{user?.name}</span>
              <button onClick={handleLogout} className="text-sm text-red-600 hover:text-red-700">
                Sign Out
              </button>
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 py-6 w-full">
        <div className="mb-6">
          <Link href="/dashboard" className="text-sm text-blue-600 hover:underline">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-2">
            {topic?.name || "Exercises"}
          </h1>
          <p className="text-gray-600">{topic?.description}</p>
        </div>

        {activeExercise ? (
          /* Exercise View */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Instructions & Code */}
            <div className="space-y-4">
              <div className="bg-white rounded-xl border p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-semibold text-lg">{activeExercise.title}</h2>
                  <button
                    onClick={() => setActiveExercise(null)}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    ← Back to list
                  </button>
                </div>
                <p className="text-gray-600 mb-4">{activeExercise.description}</p>

                {activeExercise.hints.length > 0 && (
                  <details className="text-sm">
                    <summary className="cursor-pointer text-blue-600 hover:underline">
                      Show hints
                    </summary>
                    <ul className="mt-2 space-y-1 text-gray-600">
                      {activeExercise.hints.map((hint, i) => (
                        <li key={i}>• {hint}</li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>

              <div className="h-80">
                <CodeEditor
                  initialCode={code}
                  onChange={setCode}
                  onRun={handleRunCode}
                  height="100%"
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="flex-1 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
                >
                  {isSubmitting ? "Submitting..." : "Submit Solution"}
                </button>
              </div>
            </div>

            {/* Right: Output & Feedback */}
            <div className="space-y-4">
              <div className="h-48">
                <OutputPanel output={output} error={error} isLoading={isRunning} />
              </div>

              {feedback && (
                <div className="bg-white rounded-xl border p-6">
                  <h3 className="font-semibold mb-2">Feedback</h3>
                  <pre className="text-sm whitespace-pre-wrap text-gray-700">{feedback}</pre>
                </div>
              )}

              <div className="bg-white rounded-xl border p-6">
                <h3 className="font-semibold mb-2">Test Cases</h3>
                <div className="space-y-2">
                  {activeExercise.test_cases
                    .filter((t) => !t.is_hidden)
                    .map((test, i) => (
                      <div key={i} className="text-sm p-2 bg-gray-50 rounded">
                        <p className="text-gray-500">Input: {test.input || "(none)"}</p>
                        <p className="text-gray-700">Expected: {test.expected_output}</p>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Exercise List View */
          <div>
            <div className="flex items-center gap-4 mb-6">
              <span className="text-sm text-gray-600">Generate new:</span>
              {(["beginner", "intermediate", "advanced"] as const).map((diff) => (
                <button
                  key={diff}
                  onClick={() => handleGenerateNew(diff)}
                  disabled={loading}
                  className="px-3 py-1 text-sm border rounded-lg hover:bg-gray-50 disabled:opacity-50 capitalize"
                >
                  {diff}
                </button>
              ))}
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-40 bg-gray-200 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : exercises.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {exercises.map((exercise) => (
                  <ExerciseCard
                    key={exercise.id}
                    exercise={exercise}
                    onStart={handleStartExercise}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                No exercises yet. Generate one to get started!
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
