"use client";

import React, { useEffect, useState } from "react";
import { BookOpen, Plus, FileText, Trash2, X } from "lucide-react";

interface Notebook {
  id: string;
  title: string;
  description: string;
  sources_count: number;
}

export default function NotebooksPage() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchNotebooks = () => {
    fetch(`${apiUrl}/api/notebooks`)
      .then((res) => res.json())
      .then((data) => setNotebooks(data))
      .catch((err) => console.error("Fehler beim Laden der Notizbücher:", err));
  };

  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then((data) => setHealthStatus(data))
      .catch((err) => console.error("Backend nicht erreichbar:", err));

    fetchNotebooks();
  }, [apiUrl]);

  const handleCreateNotebook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      const res = await fetch(`${apiUrl}/api/notebooks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle, description: newDesc }),
      });

      if (res.ok) {
        setNewTitle("");
        setNewDesc("");
        setIsModalOpen(false);
        fetchNotebooks();
      }
    } catch (err) {
      console.error("Fehler beim Erstellen:", err);
    }
  };

  const handleDeleteNotebook = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Notizbuch wirklich löschen?")) return;

    try {
      await fetch(`${apiUrl}/api/notebooks/${id}`, { method: "DELETE" });
      fetchNotebooks();
    } catch (err) {
      console.error("Fehler beim Löschen:", err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center border-b border-slate-800 pb-5">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Notizbücher</h2>
          <p className="text-sm text-slate-400">Verwalte deine Forschungsprojekte und Quellen.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <Plus className="h-4 w-4" /> Neues Notizbuch
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
        <div className="space-y-1">
          <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">System Status</span>
          <p className="text-sm font-medium text-slate-200">
            {healthStatus ? `Aktiv: ${healthStatus.architecture}` : "Verbinde mit Backend..."}
          </p>
        </div>
        {healthStatus && (
          <div className="flex gap-4 text-xs text-slate-400">
            <div>ChromaDB Chunks: <span className="text-slate-100 font-mono">{healthStatus.persistence?.vector_chunks ?? 0}</span></div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {notebooks.length === 0 ? (
          <div className="col-span-full bg-slate-900/50 border border-slate-800/80 rounded-xl p-8 text-center text-slate-500 text-sm">
            Keine Notizbücher vorhanden. Klicke auf "Neues Notizbuch", um eines zu erstellen.
          </div>
        ) : (
          notebooks.map((nb) => (
            <div
              key={nb.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-5 space-y-3 transition-all relative group"
            >
              <div className="flex justify-between items-start">
                <div className="p-2.5 bg-sky-500/10 text-sky-400 rounded-lg">
                  <BookOpen className="h-5 w-5" />
                </div>
                <button
                  onClick={(e) => handleDeleteNotebook(nb.id, e)}
                  className="text-slate-500 hover:text-rose-400 transition-colors opacity-0 group-hover:opacity-100"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <div>
                <h3 className="font-semibold text-slate-200">{nb.title}</h3>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">{nb.description || "Keine Beschreibung vorhanden."}</p>
              </div>
              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1.5"><FileText className="h-3.5 w-3.5" /> {nb.sources_count} Quellen</span>
                <span className="font-mono text-[10px]">ID: {nb.id.substring(0, 8)}...</span>
              </div>
            </div>
          ))
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100">Neues Notizbuch anlegen</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="h-4 w-4" />
              </button>
            </div>
            <form onSubmit={handleCreateNotebook} className="space-y-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Titel</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="z.B. KI-Forschung 2026"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Beschreibung (optional)</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Kurze Zusammenfassung..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-sky-500 h-20"
                />
              </div>
              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-semibold rounded-lg hover:bg-slate-700"
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-sky-500 text-slate-950 text-xs font-semibold rounded-lg hover:bg-sky-400"
                >
                  Erstellen
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
