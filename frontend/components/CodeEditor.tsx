"use client";

import dynamic from "next/dynamic";
import { useState, useCallback } from "react";

// Dynamic import with SSR disabled per research.md decision 5
const Editor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="h-full flex items-center justify-center bg-gray-900 text-gray-400">
      Loading editor...
    </div>
  ),
});

interface CodeEditorProps {
  initialCode?: string;
  onChange?: (code: string) => void;
  onRun?: (code: string) => void;
  readOnly?: boolean;
  height?: string;
}

export default function CodeEditor({
  initialCode = "# Write your Python code here\nprint('Hello, EmberLearn!')\n",
  onChange,
  onRun,
  readOnly = false,
  height = "400px",
}: CodeEditorProps) {
  const [code, setCode] = useState(initialCode);

  const handleEditorChange = useCallback(
    (value: string | undefined) => {
      const newCode = value || "";
      setCode(newCode);
      onChange?.(newCode);
    },
    [onChange]
  );

  const handleRun = useCallback(() => {
    onRun?.(code);
  }, [code, onRun]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <span className="text-sm text-gray-300 font-medium">Python</span>
        {onRun && (
          <button
            onClick={handleRun}
            className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
            </svg>
            Run
          </button>
        )}
      </div>
      <div className="flex-1 monaco-container" style={{ height }}>
        <Editor
          height="100%"
          defaultLanguage="python"
          theme="vs-dark"
          value={code}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            wordWrap: "on",
            readOnly,
            padding: { top: 16 },
            suggestOnTriggerCharacters: true,
            quickSuggestions: true,
          }}
        />
      </div>
    </div>
  );
}
