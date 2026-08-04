"use client";

import React, { useEffect, useState } from "react";
import { Settings, Server, Database, Cpu, CheckCircle2, XCircle, RefreshCw } from "lucide-react";

interface SystemSettings {
  environment: string;
  version: string;
  openai_api_base: string;
  llm_model_name: string;
  embedding_model_name: string;
  embedding_dimensions: number;
  llm_context_window: number;
  chunk_size: number;
  chunk_overlap: number;
  sqlite_db_path: string;
  chroma_db_path: string;
  total_vector_chunks: number;
  llm_router_online: boolean;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchSettings = () => {
    setIsLoading(true);
    fetch(`${apiUrl}/api/settings`)
      .then((res) => res.json())
      .then((data) => setSettings(data))
      .catch((err) => console.error("Fehler beim Laden der Einstellungen:", err))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchSettings();
  }, [apiUrl]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-slate-800 pb-5 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">System-Einstellungen & Status</h2>
          <p className="text-sm text-slate-400">Übersicht der Laufzeitumgebung, Pfade und Modell-Parameter.</p>
        </div>
        <button
          onClick={fetchSettings}
          className="p-2 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 rounded-lg text-xs flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} /> Aktualisieren
        </button>
      </div>

      {settings && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Karten-Segment 1: Lokaler LLM Router */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 font-semibold text-slate-200 text-sm">
                <Server className="h-4 w-4 text-sky-400" /> Lokaler LLM-Router
              </div>
              {settings.llm_router_online ? (
                <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/60 px-2.5 py-0.5 rounded-full font-medium">
                  <CheckCircle2 className="h-3 w-3" /> Online
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs text-rose-400 bg-rose-950/40 border border-rose-800/60 px-2.5 py-0.5 rounded-full font-medium">
                  <XCircle className="h-3 w-3" /> Offline / Error
                </span>
              )}
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between"><span className="text-slate-500">API Base:</span><span className="font-mono text-slate-300">{settings.openai_api_base}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Chat Modell:</span><span className="font-mono text-sky-400">{settings.llm_model_name}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Embedding Modell:</span><span className="font-mono text-slate-300">{settings.embedding_model_name}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Kontext-Fenster:</span><span className="font-mono text-slate-300">{settings.llm_context_window} Tokens</span></div>
            </div>
          </div>

          {/* Karten-Segment 2: Eingebettete Persistenz */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center gap-2 font-semibold text-slate-200 text-sm border-b border-slate-800 pb-3">
              <Database className="h-4 w-4 text-sky-400" /> Persistenzschicht
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between"><span className="text-slate-500">SQLite DB:</span><span className="font-mono text-slate-300 truncate max-w-[200px]" title={settings.sqlite_db_path}>{settings.sqlite_db_path}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">ChromaDB Pfad:</span><span className="font-mono text-slate-300 truncate max-w-[200px]" title={settings.chroma_db_path}>{settings.chroma_db_path}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Vektor-Dimensionen:</span><span className="font-mono text-sky-400">{settings.embedding_dimensions} dim</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Indizierte Chunks:</span><span className="font-mono text-slate-100 font-bold">{settings.total_vector_chunks}</span></div>
            </div>
          </div>

          {/* Karten-Segment 3: Ingestion & RAG Konfiguration */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 md:col-span-2">
            <div className="flex items-center gap-2 font-semibold text-slate-200 text-sm border-b border-slate-800 pb-3">
              <Cpu className="h-4 w-4 text-sky-400" /> RAG & Chunking Parameter
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[11px]">Chunk Size</span>
                <p className="text-sm font-mono font-bold text-slate-200">{settings.chunk_size} Tokens</p>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[11px]">Chunk Overlap</span>
                <p className="text-sm font-mono font-bold text-slate-200">{settings.chunk_overlap} Tokens</p>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[11px]">Server Version</span>
                <p className="text-sm font-mono font-bold text-sky-400">{settings.version}</p>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[11px]">Umgebung</span>
                <p className="text-sm font-mono font-bold text-slate-200 uppercase">{settings.environment}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
