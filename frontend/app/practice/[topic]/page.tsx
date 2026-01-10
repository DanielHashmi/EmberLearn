"use client";

import { useState, use } from "react";
import dynamic from "next/dynamic";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Play, MessageCircle, Info } from "lucide-react";
import Link from "next/link";

// Monaco Editor - dynamically imported to avoid SSR issues
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

export default function PracticePage({ params }: { params: Promise<{ topic: string }> }) {
  const { topic } = use(params);
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
    <div className="flex flex-col h-screen overflow-hidden pt-20">
      <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-hidden">
        {/* Left Column: Editor */}
        <div className="flex flex-col gap-4">
          <Card variant="glass" className="flex-1 flex flex-col overflow-hidden bg-glass/60 backdrop-blur-xl border-glass-border/30">
            <div className="p-4 border-b border-glass-border/20 flex justify-between items-center bg-glass/20">
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <span className="w-3 h-3 rounded-full bg-yellow-500/50" />
                main.py
              </div>
              <Button size="sm" onClick={handleRunCode} className="gap-2 bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-500/20">
                <Play size={16} /> Run Code
              </Button>
            </div>
            <div className="flex-1 relative">
              <MonacoEditor
                height="100%"
                defaultLanguage="python"
                value={code}
                onChange={(value) => setCode(value || "")}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  scrollBeyondLastLine: false,
                  padding: { top: 16, bottom: 16 },
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              />
            </div>
          </Card>

          {/* Output Console */}
          <Card variant="default" className="h-48 bg-black/90 text-green-400 font-mono text-sm p-4 overflow-auto border-glass-border/20 shadow-inner">
            <div className="flex items-center gap-2 mb-2 text-muted-foreground text-xs uppercase tracking-wider">
              <Info size={12} /> Console Output
            </div>
            <pre>{output || "> Ready to execute..."}</pre>
          </Card>
        </div>

        {/* Right Column: AI Tutor */}
        <Card variant="glass" className="flex flex-col bg-glass/40 backdrop-blur-lg border-glass-border/30">
          <div className="p-6 border-b border-glass-border/20 bg-glass/10">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <MessageCircle className="text-primary" />
              AI Assistant
            </h2>
            <p className="text-sm text-muted-foreground">Ask questions about {topic} or get help debugging.</p>
          </div>

          <div className="flex-1 p-6 overflow-y-auto space-y-4">
            {response ? (
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">🤖</div>
                <div className="bg-glass/50 p-4 rounded-2xl rounded-tl-none border border-glass-border/20 text-sm leading-relaxed">
                  {response}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground opacity-50">
                <MessageCircle size={48} className="mb-4" />
                <p>No questions asked yet.</p>
              </div>
            )}
          </div>

          <div className="p-4 bg-glass/20 border-t border-glass-border/20">
            <div className="flex gap-2">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about this code..."
                className="flex-1 p-3 bg-background/50 backdrop-blur-sm border border-glass-border/30 rounded-xl resize-none focus:ring-2 focus:ring-primary/50 focus:border-transparent h-12 min-h-[3rem]"
              />
              <Button onClick={handleAskQuestion} size="icon" className="h-auto w-12 rounded-xl">
                <ArrowUpIcon />
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function ArrowUpIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 19V5M12 5L5 12M12 5L19 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}
