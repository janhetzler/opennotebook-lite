# Roadmap (Open Notebook Lite)

This roadmap outlines planned features, improvements, and architectural goals for the Open Notebook Lite project.

## 🚀 Phase 1: Stabilization & Bugfixes (Short-Term)
The immediate focus is on resolving usability blockers and refining the RAG pipeline.
* [x] **Notebook Source Management:** Implement UI to assign uploaded documents to specific notebooks.
* [x] **Search Implementation:** Build the missing `/search` page for global full-text and semantic vector search across all indexed documents.
* [x] **Dynamic RAG Context Thresholding:** Improve the ChromaDB retrieval in `chat.py` to filter out low-relevance chunks to prevent LLM hallucination (context mixing).
* [x] **Frontend Polling/WebSockets:** Add auto-refresh capabilities to the `/sources` page so users don't have to manually reload to see when a document finishes indexing.

## 🛠️ Phase 2: Core Feature Enhancements (Medium-Term)
* [ ] **Streaming RAG Responses:** Update the FastAPI endpoint and Next.js frontend to support streaming responses (Server-Sent Events) for a more interactive chat experience.
* [ ] **Notebook Editing:** Allow users to rename and update descriptions of existing notebooks.
* [ ] **Advanced Chunking Strategies:** Implement semantic chunking or overlap tuning in the `pdf_extractor` and `source.py` graph for better context retention.
* [ ] **Source Document Preview:** Add a basic document viewer in the frontend to read the raw text that was extracted from PDFs.

## 🌌 Phase 3: Advanced Capabilities (Long-Term)
* [ ] **Multi-Agent Orchestration:** Extend the single-LLM RAG chat to support specialized sub-agents (e.g., a "Researcher" agent and a "Summarizer" agent) using LangGraph.
* [ ] **Cross-Notebook Queries:** Allow users to query multiple selected notebooks simultaneously, rather than just one or all.
* [ ] **Export & Reporting:** Generate automated research summaries and export them as markdown or PDF files.
