"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useUser } from "@/components/dashboard/user-context";
import { api } from "@/lib/api-client";
import type { ChatSource } from "@/lib/api-types";
import { Send, Loader2, Sparkles, Trash2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}

export default function ChatPage() {
  const { user, loading: userLoading } = useUser();
  const [messages, setMessages] = useState<Message[]>([]);
  const [history, setHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const introShown = useRef(false);

  // Load persisted history or show intro
  useEffect(() => {
    if (userLoading || introShown.current) return;
    introShown.current = true;

    api.me.chatHistory().then((res) => {
      if (res.messages.length > 0) {
        setMessages(res.messages.map((m) => ({ role: m.role as "user" | "assistant", content: m.content })));
        setHistory(res.messages);
      } else {
        const firstName = user?.name?.split(" ")[0] || "there";
        const deviceNames = user?.devices?.map((d) => d.model || d.vendor).join(", ") || "your devices";
        setMessages([{
          role: "assistant",
          content: `Hi ${firstName}! I'm Glymmy, your AI health companion. I have access to your CGM, ${deviceNames}, and health profile. Ask me anything — "How was my glucose today?", "Should I eat this?", or "What does my A1C mean?"`,
        }]);
      }
    }).catch(() => {
      const firstName = user?.name?.split(" ")[0] || "there";
      setMessages([{ role: "assistant", content: `Hi ${firstName}! I'm Glymmy. Ask me anything about your health data.` }]);
    });
  }, [user, userLoading]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    const userMsg: Message = { role: "user", content: text };
    setMessages((m) => [...m, userMsg]);

    const newHistory = [...history, { role: "user", content: text }];
    setLoading(true);
    try {
      const res = await api.me.chatMe(text, newHistory);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.response, sources: res.sources },
      ]);
      setHistory([...newHistory, { role: "assistant", content: res.response }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Sorry, I hit an error. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] max-w-4xl">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Ask Glymmy</h1>
          <p className="text-neutral-500 mt-1">
            AI health chat powered by Gemma 4 + your wearable data
          </p>
        </div>
        {messages.length > 1 && (
          <Button
            variant="ghost"
            size="sm"
            className="text-neutral-500 hover:text-red-400"
            onClick={async () => {
              await api.me.clearChatHistory();
              introShown.current = false;
              setMessages([]);
              setHistory([]);
              const firstName = user?.name?.split(" ")[0] || "there";
              setMessages([{ role: "assistant", content: `Chat cleared! Hi ${firstName}, what would you like to know?` }]);
            }}
          >
            <Trash2 className="h-4 w-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                m.role === "user"
                  ? "bg-sky-600 text-white"
                  : "bg-neutral-900 border border-neutral-800 text-neutral-100"
              }`}
            >
              {m.role === "assistant" && (
                <div className="flex items-center gap-1 mb-1 text-xs text-sky-400">
                  <Sparkles className="h-3 w-3" />
                  <span>Glymmy</span>
                </div>
              )}
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {m.sources.map((s, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs border-neutral-700 text-neutral-400">
                      {s.title}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl px-4 py-3 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
              <span className="text-sm text-neutral-500">Thinking...</span>
            </div>
          </div>
        )}
      </div>

      <Card className="border-neutral-800 bg-neutral-900/50 mt-4">
        <CardContent className="pt-4">
          <div className="flex gap-2">
            <Textarea
              placeholder="Ask anything about your health data..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              rows={2}
              className="flex-1 resize-none bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
            />
            <Button onClick={send} disabled={loading || !input.trim()} className="bg-sky-600 hover:bg-sky-500">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
