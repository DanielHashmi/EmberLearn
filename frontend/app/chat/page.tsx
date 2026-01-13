"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Sparkles, Code, Bug, BarChart, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { chatApi } from "@/src_lib/api";
import { withAuth } from "@/src_lib/auth-context";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "👋 Hi! I'm your Python tutor. Ask me anything about Python programming - concepts, debugging, exercises, or code review!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setLoading(true);

    try {
      const data = await chatApi.chat(currentInput);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ Connection error: ${errorMessage}\n\nMake sure the backend is running on http://localhost:8000`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleQuickAction = (text: string) => {
    setInput(text);
  };

  return (
    <div className="flex flex-col h-screen pt-24 pb-4">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8">
        <div className="max-w-3xl mx-auto space-y-4 py-4">
          <AnimatePresence mode="popLayout">
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`flex gap-3 max-w-[85%] ${
                    message.role === "user" ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-accent/20 text-accent"
                    }`}
                  >
                    {message.role === "user" ? <User size={18} /> : <Bot size={18} />}
                  </div>

                  <div
                    className={`px-4 py-3 rounded-2xl ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground rounded-tr-sm"
                        : "bg-card border border-border rounded-tl-sm"
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      {message.content}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="flex gap-3">
                <div className="w-9 h-9 rounded-full bg-accent/20 flex items-center justify-center">
                  <Bot size={18} className="text-accent" />
                </div>
                <div className="bg-card border border-border px-4 py-3 rounded-2xl rounded-tl-sm">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Loader2 size={16} className="animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="px-4 md:px-8 pt-4 border-t border-border bg-background/80 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto space-y-3">
          {/* Quick Actions */}
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            <QuickAction
              icon={<Sparkles size={14} />}
              label="Explain loops"
              onClick={() => handleQuickAction("Explain how for loops work in Python")}
            />
            <QuickAction
              icon={<Code size={14} />}
              label="Give me an exercise"
              onClick={() => handleQuickAction("Give me a coding exercise to practice")}
            />
            <QuickAction
              icon={<Bug size={14} />}
              label="Help debug"
              onClick={() => handleQuickAction("Help me debug my code")}
            />
            <QuickAction
              icon={<BarChart size={14} />}
              label="Check progress"
              onClick={() => handleQuickAction("Show my learning progress")}
            />
          </div>

          {/* Input */}
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask about Python... (Enter to send)"
              disabled={loading}
              className="flex-1 px-4 py-3 bg-card border border-border rounded-xl focus:ring-2 focus:ring-primary/50 focus:border-primary resize-none text-sm placeholder:text-muted-foreground disabled:opacity-50"
              rows={1}
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            <Button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              size="icon"
              className="h-12 w-12 rounded-xl shrink-0"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function QuickAction({ 
  icon, 
  label, 
  onClick 
}: { 
  icon: React.ReactNode
  label: string
  onClick: () => void 
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-card hover:bg-accent/10 border border-border rounded-full transition-colors whitespace-nowrap"
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}

export default withAuth(ChatPage);
