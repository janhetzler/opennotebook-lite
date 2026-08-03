# Known Bugs & Missing Features (Frontend Code Audit)

This document tracks all identified issues, unlinked UI elements, and mock components found during a comprehensive static analysis of the Next.js frontend source code (v2.0.1-light).

## 🚨 1. Navigation & Routing (Dead Links)
* **`/search` (Search Page):** The sidebar (`sidebar.tsx`) contains a link to `/search`, but no corresponding Next.js page exists in `src/app/search/page.tsx`. Clicking it results in a 404 error.
* **`/settings` (Settings Page):** The sidebar contains a link to `/settings`, but this page is also completely missing, resulting in a 404 error.

## 📓 2. Notebooks Dashboard (`page.tsx`)
* **Notebook Cards are Unclickable (No Detail View):** The notebook cards render the title, description, and source count, but they have no `onClick` handler or `<Link>` wrapper. It is impossible to "open" a notebook to see its contents.
* **No Edit Functionality:** Users can create and delete notebooks, but there is no UI to edit an existing notebook's title or description.
* **Orphaned Source Count:** The UI displays `{nb.sources_count}`, but since sources cannot be assigned to notebooks yet (see below), this number will always be 0.

## 📄 3. Sources Management (`sources/page.tsx`)
* **Missing Notebook Assignment (Critical):** The backend route `POST /api/sources/upload` accepts a `notebook_id` form field, but the frontend form in `sources/page.tsx` does not provide a dropdown to select a notebook. Files are always uploaded globally.
* **No Re-Assignment UI:** There is no UI to move an already uploaded source into a specific notebook.
* **No Auto-Refresh (Polling):** When a file is uploaded, its status is `processing`. The UI does not poll the backend for updates. Users must manually press F5 to see when it changes to `completed`.
* **No Document Preview:** There is no way to click on a source to view the extracted text or verify what was actually parsed.

## 💬 4. Chat Interface (`chat/page.tsx`)
* **Static "8k Kontext" Badge:** The badge displaying "8k Kontext" with a sparkles icon is a hardcoded UI mockup element in the frontend. It is not dynamically linked to the actual context window of the Granite model.

## 🧠 5. Backend & AI Integration
* **RAG Context Mixing (Hallucination Trigger):** The `execute_chat` endpoint in `api/routers/chat.py` blindly fetches `top_k=4` chunks. If irrelevant chunks are included, the Granite 4.0 H-Tiny model tends to hallucinate and mix contexts. Needs a distance threshold filter.
