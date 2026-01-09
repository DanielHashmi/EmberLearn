"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Sparkles, Code, Bug, BarChart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "👋 Hi! I'm your Python tutor. Ask me anything about Python programming!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const { chatApi } = await import("@/lib/api");
      const data = await chatApi.chat(input);

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
          content: `❌ Error: ${errorMessage}. Make sure the backend server is running on port 8000.`,
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

  return (
    <div className="flex flex-col h-screen overflow-hidden pt-20">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-2xl flex gap-4 ${
                  message.role === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg ${
                    message.role === "user"
                      ? "bg-primary text-white"
                      : "bg-purple-600 text-white"
                  }`}
                >
                  {message.role === "user" ? <User size={20} /> : <Bot size={20} />}
                </div>

                <Card
                  variant={message.role === "user" ? "default" : "glass"}
                  className={`p-4 rounded-2xl shadow-md ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground border-primary/20 rounded-tr-none"
                      : "rounded-tl-none border-glass-border/30 bg-glass/60 backdrop-blur-xl"
                  }`}
                >
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {message.content}
                  </div>
                </Card>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex justify-start"
          >
            <div className="bg-glass/40 backdrop-blur-md p-4 rounded-2xl rounded-tl-none border border-glass-border/20 shadow-sm ml-14">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 md:p-6 bg-glass/20 backdrop-blur-lg border-t border-glass-border/20">
        <div className="max-w-4xl mx-auto space-y-4">

          {/* Quick Actions */}
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            <QuickAction
              icon={<Sparkles size={16} />}
              label="Explain loops"
              onClick={() => setInput("How do for loops work?")}
            />
            <QuickAction
              icon={<Code size={16} />}
              label="Practice exercise"
              onClick={() => setInput("Give me a coding exercise")}
            />
            <QuickAction
              icon={<Bug size={16} />}
              label="Debug help"
              onClick={() => setInput("Debug my code")}
            />
            <QuickAction
              icon={<BarChart size={16} />}
              label="My progress"
              onClick={() => setInput("Show my progress")}
            />
          </div>

          <div className="flex gap-3 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about Python... (Shift+Enter for new line)"
              className="flex-1 p-4 pr-16 bg-white/50 dark:bg-black/50 backdrop-blur-md border border-glass-border/30 rounded-2xl focus:ring-2 focus:ring-primary/50 focus:border-transparent resize-none shadow-inner placeholder:text-muted-foreground transition-all h-16 max-h-32"
              rows={1}
            />
            <Button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="absolute right-2 top-2 h-12 w-12 rounded-xl bg-primary hover:bg-primary/90 shadow-lg hover:shadow-primary/25 hover:scale-105 transition-all"
              size="icon"
            >
              <Send size={20} />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function QuickAction({ icon, label, onClick }: { icon: React.ReactNode, label: string, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-glass/30 hover:bg-glass/50 border border-glass-border/20 rounded-full transition-all whitespace-nowrap backdrop-blur-sm text-foreground hover:scale-105 active:scale-95"
    >
      {icon}
      <span>{label}</span>
    </button>
  )
}
