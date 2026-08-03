"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, FileText, MessageSquare, Search, Settings } from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Notebooks", href: "/", icon: BookOpen },
  { label: "Sources", href: "/sources", icon: FileText },
  { label: "Chat (RAG)", href: "/chat", icon: MessageSquare },
  { label: "Search", href: "/search", icon: Search },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function SidebarNav() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 h-screen p-4 flex flex-col justify-between text-slate-100">
      <div className="space-y-6">
        <div className="px-3 py-2 border-b border-slate-800 pb-4">
          <h1 className="text-xl font-bold text-sky-400">Open Notebook</h1>
          <p className="text-xs text-slate-400 mt-1">Light Edition (IBM Granite)</p>
        </div>
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="px-3 py-2 border-t border-slate-800 text-xs text-slate-500">
        Backend: SQLite + ChromaDB
      </div>
    </aside>
  );
}
