# Known Bugs & Issues (Open Notebook Lite)

This document tracks known issues, bugs, and limitations in the current version (v2.0.1-light).

## 🐛 Frontend Issues

### 1. Missing Notebook Source Assignment
* **Status:** Open
* **Description:** Users can create and delete notebooks, but there is currently no UI mechanism to assign uploaded sources to a specific notebook. Neither the Notebook Dashboard nor the Source Upload page contains a selection dropdown or assignment tool.
* **Impact:** High. Notebooks cannot currently be used to isolate context for RAG queries.

### 2. Search Page Returns 404
* **Status:** Open
* **Description:** The sidebar navigation contains a link to `/search`, but the corresponding Next.js page has not been implemented. Clicking it results in a 404 Not Found error.
* **Impact:** Medium.

### 3. Missing Auto-Refresh for Processing Status
* **Status:** Open
* **Description:** When uploading a new document on the `/sources` page, the status badge shows `processing`. When the background task finishes embedding the document into ChromaDB, the UI does not automatically update to `completed`.
* **Workaround:** Users must manually refresh the page (F5) to see the updated status.
* **Impact:** Low (UX issue).

## 🧠 Backend & AI Issues

### 1. RAG Context Mixing (Hallucination Trigger)
* **Status:** Open
* **Description:** The `execute_chat` endpoint in `api/routers/chat.py` currently fetches a hardcoded `top_k=4` chunks from ChromaDB. If the user's query only heavily matches one chunk, the system still passes the three other (potentially unrelated) chunks to the Granite LLM. Due to the small size of the Granite 4.0 H-Tiny model, it struggles to strictly adhere to the system prompt and sometimes hallucinates by mixing information from the unrelated chunks into the final answer.
* **Proposed Solution:** Implement a dynamic threshold filter. Instead of blindly passing 4 chunks, filter out chunks that exceed a specific cosine distance threshold (e.g., `distance > 0.3`), or dynamically adjust `top_k` based on score variance.
* **Impact:** Medium. RAG retrieval works perfectly, but the context assembly needs tuning.
