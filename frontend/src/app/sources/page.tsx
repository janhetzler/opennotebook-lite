"use client";

import React, { useState, useEffect } from "react";
import { Upload, CheckCircle2, AlertCircle, Loader2, FileText, Trash2 } from "lucide-react";

interface Source {
  id: string;
  title: string;
  source_type: string;
  processing_status: string;
}

export default function SourcesPage() {
  const [file, setFile] = useState<File | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [statusMessage, setStatusMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchSources = () => {
    fetch(`${apiUrl}/api/sources`)
      .then((res) => res.json())
      .then((data) => setSources(data))
      .catch((err) => console.error("Fehler beim Laden der Quellen:", err));
  };

  useEffect(() => {
    fetchSources();
  }, [apiUrl]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setStatusMessage(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${apiUrl}/api/sources/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (response.ok) {
        setStatusMessage({
          type: "success",
          text: `Datei "${data.title}" erfolgreich hochgeladen! Status: ${data.processing_status}`,
        });
        setFile(null);
        fetchSources();
      } else {
        setStatusMessage({
          type: "error",
          text: data.detail || "Fehler beim Upload der Datei.",
        });
      }
    } catch (err) {
      setStatusMessage({
        type: "error",
        text: "Netzwerkfehler: Backend unter http://localhost:8000 nicht erreichbar.",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteSource = async (id: string) => {
    if (!confirm("Quelle und Vektor-Embeddings wirklich löschen?")) return;

    try {
      await fetch(`${apiUrl}/api/sources/${id}`, { method: "DELETE" });
      fetchSources();
    } catch (err) {
      console.error("Fehler beim Löschen:", err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-slate-800 pb-5">
        <h2 className="text-2xl font-bold tracking-tight">Quellen & Dokumente</h2>
        <p className="text-sm text-slate-400">Importiere digitale Textdokumente (.pdf, .txt, .md) für die Vektor-Indizierung.</p>
      </div>

      <form onSubmit={handleUpload} className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="border-2 border-dashed border-slate-700 hover:border-sky-500/50 rounded-lg p-8 text-center space-y-3 transition-colors">
          <Upload className="h-8 w-8 text-slate-400 mx-auto" />
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-200">
              {file ? file.name : "Klicke zum Auswählen oder ziehe eine Datei hierher"}
            </p>
            <p className="text-xs text-slate-500">Nur digitale Textdokumente (PDF, TXT, MD, HTML). Keine Scans/Bilder.</p>
          </div>
          <input
            type="file"
            accept=".pdf,.txt,.md,.markdown,.html"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="inline-block bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3.5 py-2 rounded-md cursor-pointer transition-colors"
          >
            Datei auswählen
          </label>
        </div>

        <button
          type="submit"
          disabled={!file || isUploading}
          className="w-full bg-sky-500 hover:bg-sky-400 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-semibold py-2.5 rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
        >
          {isUploading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Verarbeite & Indiziere Chunks...
            </>
          ) : (
            "Dokument verarbeiten & indizieren"
          )}
        </button>
      </form>

      {statusMessage && (
        <div
          className={`p-4 rounded-xl border flex items-center gap-3 text-sm ${
            statusMessage.type === "success"
              ? "bg-emerald-950/30 border-emerald-800/50 text-emerald-400"
              : "bg-rose-950/30 border-rose-800/50 text-rose-400"
          }`}
        >
          {statusMessage.type === "success" ? <CheckCircle2 className="h-5 w-5 shrink-0" /> : <AlertCircle className="h-5 w-5 shrink-0" />}
          <span>{statusMessage.text}</span>
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="font-semibold text-slate-200 text-sm">Hochgeladene Quellen ({sources.length})</h3>
        </div>
        {sources.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">Noch keine Quellen hochgeladen.</div>
        ) : (
          <div className="divide-y divide-slate-800">
            {sources.map((src) => (
              <div key={src.id} className="p-4 flex items-center justify-between text-sm hover:bg-slate-800/40 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-slate-800 text-sky-400 rounded-lg">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-200">{src.title}</p>
                    <span className="text-xs text-slate-500 uppercase font-mono">{src.source_type}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                      src.processing_status === "completed"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : src.processing_status === "processing"
                        ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                        : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                    }`}
                  >
                    {src.processing_status}
                  </span>
                  <button
                    onClick={() => handleDeleteSource(src.id)}
                    className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
