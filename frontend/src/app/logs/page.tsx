"use client";

import React, { useEffect, useState, useRef } from "react";
import { Terminal, Download, Github, RefreshCw, Trash2, CheckCircle2 } from "lucide-react";

interface LogsResponse {
  logs: string;
  github_token_configured: boolean;
}

export default function LogsPage() {
  const [logs, setLogs] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportUrl, setExportUrl] = useState<string | null>(null);
  const [hasToken, setHasToken] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  
  const preRef = useRef<HTMLPreElement>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/logs`);
      const data: LogsResponse = await res.json();
      setLogs(data.logs);
      setHasToken(data.github_token_configured);
    } catch (err) {
      console.error("Fehler beim Laden der Logs:", err);
      setLogs("Fehler beim Laden der Logs. Ist das Backend erreichbar?");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    
    // Optional: Einfaches Polling alle 10 Sekunden, falls gewünscht
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  useEffect(() => {
    if (autoScroll && preRef.current) {
      preRef.current.scrollTop = preRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const handleDownload = () => {
    window.open(`${apiUrl}/api/logs/download`, "_blank");
  };

  const handleGithubExport = async () => {
    setIsExporting(true);
    setExportUrl(null);
    try {
      const res = await fetch(`${apiUrl}/api/logs/github`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        setExportUrl(data.url);
      } else {
        alert(`Export fehlgeschlagen: ${data.detail}`);
      }
    } catch (err) {
      console.error(err);
      alert("Netzwerkfehler beim Export.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-4 h-[calc(100vh-4rem)] flex flex-col">
      <div className="flex justify-between items-center bg-slate-900 p-4 rounded-xl border border-slate-800">
        <div className="flex items-center gap-3">
          <Terminal className="h-5 w-5 text-sky-400" />
          <h2 className="text-lg font-bold">System Console</h2>
          <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Live
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-xs text-slate-300 mr-2 cursor-pointer select-none">
            <input 
              type="checkbox" 
              checked={autoScroll} 
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="accent-sky-500 cursor-pointer"
            />
            Auto-scroll
          </label>
          
          <button
            onClick={fetchLogs}
            className="p-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs flex items-center gap-1.5 transition-colors border border-slate-700"
            title="Aktualisieren"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} /> 
          </button>
          
          <button
            onClick={() => setLogs("")}
            className="p-1.5 px-3 bg-slate-800 hover:bg-rose-900/50 text-slate-200 hover:text-rose-400 rounded-lg text-xs flex items-center gap-1.5 transition-colors border border-slate-700 hover:border-rose-800"
            title="Konsole leeren (nur im Browser)"
          >
            <Trash2 className="h-3.5 w-3.5" /> Clear
          </button>

          <button
            onClick={handleDownload}
            className="p-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs flex items-center gap-1.5 transition-colors border border-slate-700"
          >
            <Download className="h-3.5 w-3.5" /> Download
          </button>
          
          <button
            onClick={handleGithubExport}
            disabled={!hasToken || isExporting}
            className={`p-1.5 px-3 rounded-lg text-xs flex items-center gap-1.5 transition-colors border ${
              !hasToken 
                ? "bg-slate-900/50 text-slate-600 border-slate-800 cursor-not-allowed" 
                : "bg-indigo-950/60 hover:bg-indigo-900/80 text-indigo-300 border-indigo-800/60"
            }`}
            title={!hasToken ? "GITHUB_TOKEN fehlt in der .env Datei" : "Als geheimes Gist nach GitHub pushen"}
          >
            <Github className={`h-3.5 w-3.5 ${isExporting ? "animate-bounce" : ""}`} /> 
            {isExporting ? "Exportiert..." : "Nach GitHub"}
          </button>
        </div>
      </div>
      
      {exportUrl && (
        <div className="bg-emerald-950/40 border border-emerald-900/50 rounded-lg p-3 flex justify-between items-center text-sm">
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle2 className="h-4 w-4" />
            <span>Erfolgreich nach GitHub exportiert!</span>
          </div>
          <a href={exportUrl} target="_blank" rel="noreferrer" className="text-emerald-300 hover:text-emerald-200 underline text-xs">
            Gist im Browser öffnen &rarr;
          </a>
        </div>
      )}

      <div className="flex-1 bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-inner relative">
        <pre 
          ref={preRef}
          className="h-full w-full p-4 overflow-auto text-[11px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed custom-scrollbar"
        >
          {logs || "Warte auf Logs..."}
        </pre>
      </div>
    </div>
  );
}
