"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getUser, logout } from "@/lib/auth";
import { api } from "@/lib/api";
import type { ProgressDashboard } from "@/lib/types";
import MasteryCard from "@/components/MasteryCard";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ id: string; name: string; email: string } | null>(null);
  const [progress, setProgress] = useState<ProgressDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const currentUser = getUser();
    if (!currentUser) {
      router.push("/login");
      return;
    }
    setUser(currentUser);

    api
      .getProgress(currentUser.id)
      .then(setProgress)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [router]);

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-bold text-blue-600">
            EmberLearn
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/practice" className="text-gray-600 hover:text-gray-900">
              Practice
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
      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name?.split(" ")[0]}!
          </h1>
          <p className="text-gray-600">
            Continue your Python learning journey. You&apos;re making great progress!
          </p>
        </div>

        {/* Stats Overview */}
        {progress && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-xl border">
              <p className="text-sm text-gray-500 mb-1">Overall Mastery</p>
              <p className="text-3xl font-bold text-blue-600">{progress.overall_mastery}%</p>
            </div>
            <div className="bg-white p-6 rounded-xl border">
              <p className="text-sm text-gray-500 mb-1">Exercises Completed</p>
              <p className="text-3xl font-bold text-green-600">
                {progress.total_exercises_completed}
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl border">
              <p className="text-sm text-gray-500 mb-1">Current Streak</p>
              <p className="text-3xl font-bold text-orange-500">{progress.streak_days} days</p>
            </div>
            <div className="bg-white p-6 rounded-xl border">
              <p className="text-sm text-gray-500 mb-1">Time Spent</p>
              <p className="text-3xl font-bold text-purple-600">
                {Math.round(progress.total_time_spent_minutes / 60)}h
              </p>
            </div>
          </div>
        )}

        {/* Topic Mastery Grid */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Topic Mastery</h2>
          {progress ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {progress.topics.map((topic) => (
                <MasteryCard
                  key={topic.topic_id}
                  topicName={topic.topic_name}
                  masteryScore={topic.mastery_score}
                  masteryLevel={topic.mastery_level}
                  exercisesCompleted={topic.exercises_completed}
                  exercisesTotal={topic.exercises_total}
                  lastActivity={topic.last_activity}
                  onClick={() => router.push(`/exercises/${topic.topic_id}`)}
                />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-xl animate-pulse" />
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/practice"
            className="p-6 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition"
          >
            <h3 className="text-lg font-semibold mb-2">Practice Coding</h3>
            <p className="text-blue-100 text-sm">
              Write Python code and get instant feedback from AI tutors
            </p>
          </Link>
          <Link
            href="/exercises/variables"
            className="p-6 bg-green-600 text-white rounded-xl hover:bg-green-700 transition"
          >
            <h3 className="text-lg font-semibold mb-2">Start Exercises</h3>
            <p className="text-green-100 text-sm">
              Complete challenges to improve your mastery scores
            </p>
          </Link>
        </div>
      </main>
    </div>
  );
}
