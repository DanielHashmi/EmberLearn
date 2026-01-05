import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-4xl text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Welcome to <span className="text-blue-600">EmberLearn</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered Python tutoring that adapts to your learning style.
          Get personalized guidance from 6 specialized AI agents.
        </p>

        <div className="flex gap-4 justify-center mb-12">
          <Link
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 transition"
          >
            Get Started
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="p-6 bg-white rounded-xl shadow-sm border">
            <h3 className="font-semibold text-lg mb-2">Personalized Learning</h3>
            <p className="text-gray-600 text-sm">
              AI agents track your progress and adapt explanations to your skill level.
            </p>
          </div>
          <div className="p-6 bg-white rounded-xl shadow-sm border">
            <h3 className="font-semibold text-lg mb-2">Interactive Coding</h3>
            <p className="text-gray-600 text-sm">
              Write and execute Python code directly in your browser with instant feedback.
            </p>
          </div>
          <div className="p-6 bg-white rounded-xl shadow-sm border">
            <h3 className="font-semibold text-lg mb-2">Track Mastery</h3>
            <p className="text-gray-600 text-sm">
              Visual progress tracking across 8 Python topics from beginner to mastered.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
