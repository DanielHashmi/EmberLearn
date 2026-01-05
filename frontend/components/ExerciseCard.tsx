import type { Exercise } from "@/lib/types";

interface ExerciseCardProps {
  exercise: Exercise;
  onStart: (exercise: Exercise) => void;
}

export default function ExerciseCard({ exercise, onStart }: ExerciseCardProps) {
  const difficultyColors = {
    beginner: "bg-green-100 text-green-800",
    intermediate: "bg-yellow-100 text-yellow-800",
    advanced: "bg-red-100 text-red-800",
  };

  return (
    <div className="bg-white rounded-xl border p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-lg text-gray-900">{exercise.title}</h3>
        <span
          className={`px-2 py-1 text-xs font-medium rounded-full ${
            difficultyColors[exercise.difficulty]
          }`}
        >
          {exercise.difficulty}
        </span>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">{exercise.description}</p>

      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">
          {exercise.test_cases.filter((t) => !t.is_hidden).length} test cases
        </span>
        <button
          onClick={() => onStart(exercise)}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition"
        >
          Start
        </button>
      </div>
    </div>
  );
}
