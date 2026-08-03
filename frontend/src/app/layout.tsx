import React from "react";
import { SidebarNav } from "@/components/navigation/sidebar";

export const metadata = {
  title: "Open Notebook Light",
  description: "Minimalist Research Engine with Local RAG",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body className="bg-slate-950 text-slate-100 min-h-screen flex antialiased">
        <SidebarNav />
        <main className="flex-1 p-8 overflow-y-auto">{children}</main>
      </body>
    </html>
  );
}
