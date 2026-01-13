"use client";

import { useState, use } from "react";
import dynamic from "next/dynamic";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Play, Send, Loader2, Terminal, MessageCircle, CheckCircle, XCircle } from "lucide-react";
import { sandboxApi, chatApi } from "@/src_lib/api";
import { withAuth } from "@/src_lib/auth-context";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { 
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-[#1e1e1e]">
      <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
    </div>
  )
});

// ... starterCodes definition ...

function PracticePage({ params }: { params: Promise<{ topic: string }> }) {
  const { topic } = use(params);
  const [code, setCode] = useState(starterCodes[topic] || starterCodes.basics);
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [runSuccess, setRunSuccess] = useState<boolean | null>(null);
  const [question, setQuestion] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [isAsking, setIsAsking] = useState(false);

  const topicNames: Record<string, string> = {
    basics: "Python Basics",
    'control-flow': "Control Flow",
    'data-structures': "Data Structures",
    functions: "Functions",
    oop: "OOP",
  };

  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput("");
    setRunSuccess(null);
    try {
      const result = await sandboxApi.execute(code);
      if (result.success) {
        setOutput(result.output);
        setRunSuccess(true);
      } else {
        setOutput(`Error: ${result.error}`);
        setRunSuccess(false);
      }
    } catch (error) {
      setOutput(`Connection error. Is the backend running?`);
      setRunSuccess(false);
    } finally {
      setIsRunning(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim() || isAsking) return;
    setIsAsking(true);
    try {
      const msg = `Code:\n${code}\n\nQuestion: ${question}`;
      const result = await chatApi.chat(msg);
      setAiResponse(result.response);
    } catch (error) {
      setAiResponse("Error connecting to AI. Is the backend running?");
    } finally {
      setIsAsking(false);
      setQuestion("");
    }
  };

  return (
    <div className="h-screen pt-20 pb-4 px-4">
      <div className="h-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="flex flex-col gap-4 min-h-0">
          <Card className="flex-1 flex flex-col overflow-hidden border-border">
            <div className="px-4 py-3 border-b border-border flex justify-between items-center bg-card">
              <span className="text-sm font-medium">{topicNames[topic] || "Python"}</span>
              <Button size="sm" onClick={handleRunCode} disabled={isRunning}>
                {isRunning ? <Loader2 size={14} className="animate-spin mr-2" /> : <Play size={14} className="mr-2" />}
                Run
              </Button>
            </div>
            <div className="flex-1 min-h-0">
              <MonacoEditor
                height="100%"
                defaultLanguage="python"
                value={code}
                onChange={(v) => setCode(v || "")}
                theme="vs-dark"
                options={{ minimap: { enabled: false }, fontSize: 14, padding: { top: 16 } }}
              />
            </div>
          </Card>
          <Card className="h-36 flex flex-col border-border">
            <div className="px-4 py-2 border-b border-border flex items-center gap-2 bg-card">
              <Terminal size={14} />
              <span className="text-xs font-medium uppercase">Output</span>
              {runSuccess !== null && (runSuccess ? <CheckCircle size={14} className="text-green-500 ml-auto" /> : <XCircle size={14} className="text-red-500 ml-auto" />)}
            </div>
            <div className="flex-1 p-3 overflow-auto bg-[#0d1117] font-mono text-sm">
              <pre className={runSuccess === false ? 'text-red-400' : 'text-green-400'}>{output || "Click Run to execute..."}</pre>
            </div>
          </Card>
        </div>
        <Card className="flex flex-col border-border min-h-0">
          <div className="px-4 py-3 border-b border-border bg-card">
            <div className="flex items-center gap-2">
              <MessageCircle size={18} className="text-primary" />
              <h2 className="font-semibold">AI Assistant</h2>
            </div>
          </div>
          <div className="flex-1 p-4 overflow-y-auto">
            {aiResponse ? (
              <div className="bg-card border border-border p-4 rounded-xl text-sm whitespace-pre-wrap">{aiResponse}</div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <MessageCircle size={32} className="mb-2 opacity-30" />
                <p className="text-sm">Ask about your code</p>
              </div>
            )}
          </div>
          <div className="p-4 border-t border-border">
            <div className="flex gap-2">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAskQuestion()}
                placeholder="Ask a question..."
                className="flex-1 px-4 py-2 bg-background border border-border rounded-xl text-sm"
              />
              <Button onClick={handleAskQuestion} disabled={isAsking} size="icon">
                {isAsking ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default withAuth(PracticePage);
