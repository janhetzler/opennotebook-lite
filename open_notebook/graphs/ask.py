"""
Open Notebook Light - RAG Vektor-Such-Graph
Modul: open_notebook/graphs/ask.py
Zweck: Ausführung von Kosinus-Ähnlichkeitssuchen in ChromaDB für gegebene Anfragen.
Version: 2.0.0-light
"""
__version__ = "2.0.0-light"

import os
from typing import Any, Dict, List
from open_notebook.ai.models import get_default_embedding_model
from open_notebook.database.vector_store import vector_store

RAG_TOP_K_CHUNKS = int(os.getenv("RAG_TOP_K_CHUNKS", "4"))

async def execute_rag_vector_search(
    query: str,
    notebook_id: str,
    top_k: int = RAG_TOP_K_CHUNKS,
    max_distance: float = 1.0,
) -> List[Dict[str, Any]]:
    if not query or not query.strip():
        return []

    embedder = await get_default_embedding_model()
    query_embedding = await embedder.aembed_query(query)

    fetch_limit = top_k * 5 if max_distance < 1.0 else top_k
    search_results = await vector_store.search(
        query_embedding=query_embedding,
        notebook_id=notebook_id,
        limit=fetch_limit,
    )
    
    filtered = [r for r in search_results if r["distance"] <= max_distance]
    return filtered[:top_k]
