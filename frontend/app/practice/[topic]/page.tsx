"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

// Monaco Editor - dynamically imported to avoid SSR issues
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

export default function PracticePage({ params }: { params: { topic: string } }) {
  const [code, setCode] = useState("# Write your Python code here\nprint('Hello, World!')");
  const [output, setOutput] = useState("");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");

  const handleRunCode = async () => {
    // TODO: Call code execution API
    setOutput("Code execution results will appear here");
  };

  const handleAskQuestion = async () => {
    // TODO: Call AI agent API
    setResponse("AI tutor response will appear here");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-6">Practice: {params.topic}</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Code Editor */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold mb-4">Code Editor</h2>
            <MonacoEditor
              height="400px"
              defaultLanguage="python"
              value={code}
              onChange={(value) => setCode(value || "")}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
              }}
            />
            <button
              onClick={handleRunCode}
              className="mt-4 px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Run Code
            </button>

            {output && (
              <div className="mt-4 p-4 bg-gray-900 text-gray-100 rounded font-mono text-sm">
                <pre>{output}</pre>
              </div>
            )}
          </div>

          {/* AI Tutor Chat */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold mb-4">Ask AI Tutor</h2>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about Python..."
              className="w-full h-32 p-3 border rounded resize-none"
            />
            <button
              onClick={handleAskQuestion}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Ask Question
            </button>

            {response && (
              <div className="mt-4 p-4 bg-blue-50 rounded">
                <p className="text-gray-800">{response}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
