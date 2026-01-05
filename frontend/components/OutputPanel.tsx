interface OutputPanelProps {
  output: string;
  error?: string;
  isLoading?: boolean;
  executionTime?: number;
}

export default function OutputPanel({
  output,
  error,
  isLoading = false,
  executionTime,
}: OutputPanelProps) {
  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <span className="text-sm text-gray-300 font-medium">Output</span>
        {executionTime !== undefined && (
          <span className="text-xs text-gray-500">
            Executed in {executionTime}ms
          </span>
        )}
      </div>
      <div className="flex-1 p-4 overflow-auto">
        {isLoading ? (
          <div className="flex items-center gap-2 text-gray-400">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Running...
          </div>
        ) : error ? (
          <pre className="text-red-400 font-mono text-sm whitespace-pre-wrap">
            {error}
          </pre>
        ) : output ? (
          <pre className="text-green-400 font-mono text-sm whitespace-pre-wrap">
            {output}
          </pre>
        ) : (
          <span className="text-gray-500 text-sm">
            Run your code to see output here
          </span>
        )}
      </div>
    </div>
  );
}
