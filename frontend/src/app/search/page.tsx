"use client";

import React, { useState, useEffect } from "react";
import { Search, BookOpen, FileText, Sparkles, Loader2 } from "lucide-react";

interface SearchResult {
  chunk_id: string;
  source_id: string;
  text: string;
  score: number;
  distance: number;
}

interface Notebook {
  id: string;
  title: string;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [selectedNotebookId, setSelectedNotebookId] = useState<string>("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${apiUrl}/api/notebooks`)
      .then((res) => res.json())
      .then((data) => setNotebooks(data))
      .catch((err) => console.error("Fehler beim Laden der Notizbücher:", err));
  }, [apiUrl]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isSearching) return;

    setIsSearching(true);
    setHasSearched(true);

    try {
      const url = new URL(`${apiUrl}/api/search`);
      url.searchParams.append("q", query.trim());
      if (selectedNotebookId) {
        url.searchParams.append("notebook_id", selectedNotebookId);
      }

      const res = await fetch(url.toString());
      const data = await res.json();

      if (res.ok) {
        setResults(data.results || []);
      } else {
        console.error("Suchfehler:", data.detail);
        setResults([]);
      }
    } catch (err) {
      console.error("Netzwerkfehler bei der Suche:", err);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-slate-800 pb-5">
        <h2 className="text-2xl font-bold tracking-tight">Globale Vektorsuche</h2>
        <p className="text-sm text-slate-400">Durchsuche alle indizierten Dokumenten-Chunks semantisch via IBM Granite Embedding 107M.</p>
      </div>

      {/* Suchformular */}
      <form onSubmit={handleSearch} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="h-4 w-4 absolute left-3.5 top-3.5 text-slate-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Semantischen Suchbegriff eingeben (z.B. Vektordatenbanken)..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500 transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={!query.trim() || isSearching}
            className="bg-sky-500 hover:bg-sky-400 disabled:bg-slate-800 text-slate-950 font-semibold px-5 py-2.5 rounded-lg text-sm transition-colors flex items-center gap-2"
          >
            {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            Suchen
          </button>
        </div>

        {/* Notizbuch-Filter */}
        <div className="flex items-center gap-2 text-xs text-slate-400 pt-1">
          <BookOpen className="h-3.5 w-3.5 text-sky-400" />
          <span>Notizbuch-Filter:</span>
          <select
            value={selectedNotebookId}
            onChange={(e) => setSelectedNotebookId(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-md px-2.5 py-1 text-slate-300 focus:outline-none cursor-pointer"
          >
            <option value="">Alle Notizbücher (Global)</option>
            {notebooks.map((nb) => (
              <option key={nb.id} value={nb.id}>
                {nb.title}
              </option>
            ))}
          </select>
        </div>
      </form>

      {/* Ergebnisse */}
      <div className="space-y-3">
        {hasSearched && (
          <div className="flex justify-between items-center text-xs text-slate-400 px-1">
            <span>{results.length} relevante Chunks gefunden</span>
            <span className="flex items-center gap-1 text-sky-400"><Sparkles className="h-3 w-3" /> Granite 384-dim Cosine Match</span>
          </div>
        )}

        {results.length === 0 && hasSearched && !isSearching && (
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-8 text-center text-slate-500 text-sm">
            Keine passenden Vektor-Passagen gefunden. Versuche einen anderen Begriff.
          </div>
        )}

        {results.map((item, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2 hover:border-slate-700 transition-colors">
            <div className="flex justify-between items-center text-xs text-slate-500 border-b border-slate-800/80 pb-2">
              <span className="flex items-center gap-1.5 font-mono text-slate-400">
                <FileText className="h-3.5 w-3.5 text-sky-400" /> Chunk: {item.chunk_id}
              </span>
              <div className="flex items-center gap-3">
                <span className="text-slate-500 font-mono">Distanz: {item.distance}</span>
                <span className="bg-sky-500/10 text-sky-400 border border-sky-500/20 px-2 py-0.5 rounded text-[11px] font-semibold">
                  Match: {(item.score * 100).toFixed(1)}%
                </span>
              </div>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">{item.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
