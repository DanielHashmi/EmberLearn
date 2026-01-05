import { MasteryLevel, getMasteryColor } from "@/lib/types";

interface MasteryCardProps {
  topicName: string;
  masteryScore: number;
  masteryLevel: MasteryLevel;
  exercisesCompleted: number;
  exercisesTotal: number;
  lastActivity?: string;
  onClick?: () => void;
}

export default function MasteryCard({
  topicName,
  masteryScore,
  masteryLevel,
  exercisesCompleted,
  exercisesTotal,
  lastActivity,
  onClick,
}: MasteryCardProps) {
  const color = getMasteryColor(masteryLevel);

  const colorClasses = {
    red: "bg-red-100 border-red-300 text-red-800",
    yellow: "bg-yellow-100 border-yellow-300 text-yellow-800",
    green: "bg-green-100 border-green-300 text-green-800",
    blue: "bg-blue-100 border-blue-300 text-blue-800",
  };

  const progressColors = {
    red: "bg-red-500",
    yellow: "bg-yellow-500",
    green: "bg-green-500",
    blue: "bg-blue-500",
  };

  const levelLabels = {
    beginner: "Beginner",
    learning: "Learning",
    proficient: "Proficient",
    mastered: "Mastered",
  };

  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-xl border-2 ${colorClasses[color]} ${
        onClick ? "cursor-pointer hover:shadow-md transition-shadow" : ""
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-lg">{topicName}</h3>
        <span className="text-2xl font-bold">{masteryScore}%</span>
      </div>

      <div className="mb-3">
        <div className="h-2 bg-white/50 rounded-full overflow-hidden">
          <div
            className={`h-full ${progressColors[color]} transition-all duration-500`}
            style={{ width: `${masteryScore}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">{levelLabels[masteryLevel]}</span>
        <span className="opacity-75">
          {exercisesCompleted}/{exercisesTotal} exercises
        </span>
      </div>

      {lastActivity && (
        <p className="mt-2 text-xs opacity-60">
          Last activity: {new Date(lastActivity).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}
