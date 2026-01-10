"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Topic {
  id: number;
  name: string;
  slug: string;
  description: string;
  masteryScore: number;
}

export default function Dashboard() {
  const [topics, setTopics] = useState<Topic[]>([]);

  useEffect(() => {
    // TODO: Fetch from API
    setTopics([
      { id: 1, name: "Python Basics", slug: "basics", description: "Variables, types, operators", masteryScore: 75 },
      { id: 2, name: "Control Flow", slug: "control-flow", description: "If, loops, conditionals", masteryScore: 60 },
      { id: 3, name: "Data Structures", slug: "data-structures", description: "Lists, dicts, sets", masteryScore: 45 },
    ]);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Your Learning Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topics.map((topic) => (
            <Link key={topic.id} href={`/practice/${topic.slug}`}>
              <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
                <h3 className="text-xl font-semibold mb-2">{topic.name}</h3>
                <p className="text-gray-600 mb-4">{topic.description}</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${topic.masteryScore}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{topic.masteryScore}%</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
