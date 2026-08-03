"use client";

import React, { useState, useEffect } from "react";
import { Send, Bot, User, Sparkles, BookOpen, FileText } from "lucide-react";

interface SourceUsed {
  chunk_id: string;
  content: string;
  score: number;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources_used?: SourceUsed[];
}

interface Notebook {
  id: string;
  title: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hallo! Ich bin dein lokaler Forschungsassistent (IBM Granite 4.0 H-Tiny). Stelle mir eine Frage zu deinen indizierten Dokumenten.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [selectedNotebookId, setSelectedNotebookId] = useState<string>("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${apiUrl}/api/notebooks`)
      .then((res) => res.json())
      .then((data) => setNotebooks(data))
      .catch((err) => console.error("Fehler beim Laden der Notizbücher:", err));
  }, [apiUrl]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg,
          notebook_id: selectedNotebookId || null,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: data.response,
            sources_used: data.sources_used,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Fehler: ${data.detail || "Antwort konnte nicht generiert werden."}`,
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Netzwerkfehler: Backend ist nicht erreichbar.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-6rem)] flex flex-col justify-between space-y-4">
      <div className="border-b border-slate-800 pb-4 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">RAG Chat</h2>
          <p className="text-sm text-slate-400">Interagiere mit deinen Quellen via IBM Granite 4.0 H-Tiny.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300">
            <BookOpen className="h-3.5 w-3.5 text-sky-400" />
            <select
              value={selectedNotebookId}
              onChange={(e) => setSelectedNotebookId(e.target.value)}
              className="bg-transparent focus:outline-none cursor-pointer"
            >
              <option value="">Alle Quellen (Global)</option>
              {notebooks.map((nb) => (
                <option key={nb.id} value={nb.id} className="bg-slate-900">
                  {nb.title}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-1.5 text-xs bg-sky-500/10 text-sky-400 border border-sky-500/20 px-3 py-1.5 rounded-full">
            <Sparkles className="h-3.5 w-3.5" /> 8k Kontext
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 p-4 rounded-xl text-sm ${
              msg.role === "user" ? "bg-slate-900 border border-slate-800 ml-12" : "bg-slate-900/40 border border-slate-800/60 mr-12"
            }`}
          >
            <div className={`p-2 rounded-lg h-fit ${msg.role === "user" ? "bg-sky-500 text-slate-950" : "bg-slate-800 text-sky-400"}`}>
              {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>
            <div className="space-y-2 flex-1">
              <span className="text-xs font-semibold text-slate-400">{msg.role === "user" ? "Du" : "Granite AI"}</span>
              <p className="text-slate-200 leading-relaxed whitespace-pre-wrap">{msg.content}</p>

              {msg.sources_used && msg.sources_used.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2">
                  <span className="text-xs font-semibold text-slate-500 flex items-center gap-1.5">
                    <FileText className="h-3 w-3" /> Genutzte Dokumenten-Passagen ({msg.sources_used.length}):
                  </span>
                  <div className="grid grid-cols-1 gap-1.5">
                    {msg.sources_used.map((src, sIdx) => (
                      <div key={sIdx} className="bg-slate-950/60 border border-slate-800/60 rounded-lg p-2.5 text-xs text-slate-400">
                        <div className="flex justify-between text-[10px] text-slate-500 mb-1">
                          <span>Chunk ID: {src.chunk_id}</span>
                          <span className="text-sky-400/80">Match: {(src.score * 100).toFixed(1)}%</span>
                        </div>
                        <p className="line-clamp-2 italic text-slate-300">"{src.content}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 p-4 rounded-xl text-sm bg-slate-900/40 border border-slate-800/60 mr-12 animate-pulse">
            <div className="p-2 rounded-lg bg-slate-800 text-sky-400 h-fit">
              <Bot className="h-4 w-4" />
            </div>
            <div className="text-slate-400 text-xs flex items-center">IBM Granite verarbeitet Kontext & generiert Antwort...</div>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Frage an deine Dokumente stellen..."
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-sky-500/50 transition-colors"
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="bg-sky-500 hover:bg-sky-400 disabled:bg-slate-800 text-slate-950 font-semibold px-5 py-3 rounded-xl transition-colors"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
