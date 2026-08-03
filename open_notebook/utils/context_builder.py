"""
Open Notebook Light - Dual-Fetch Kontext-Assembler
Modul: open_notebook/utils/context_builder.py
Zweck: Konsolidiert Metadaten aus SQLite und relevante Vektor-Chunks aus ChromaDB zu einem Prompt-Payload.
Version: 2.0.0-light
"""
__version__ = "2.0.0-light"

import os
from typing import Any, Dict, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from open_notebook.ai.models import get_default_embedding_model
from open_notebook.database.sqlite_client import sqlite_client
from open_notebook.database.models_sqlite import NotebookModel
from open_notebook.database.vector_store import vector_store

RAG_TOP_K_CHUNKS = int(os.getenv("RAG_TOP_K_CHUNKS", "4"))

async def build_context_for_chat(
    notebook_id: str,
    query: str = "",
    top_k_chunks: int = RAG_TOP_K_CHUNKS,
) -> Dict[str, Any]:
    sources_metadata: List[Dict[str, Any]] = []
    notes_data: List[Dict[str, Any]] = []

    async with sqlite_client.session() as session:
        stmt = (
            select(NotebookModel)
            .options(
                selectinload(NotebookModel.sources),
                selectinload(NotebookModel.notes),
            )
            .where(NotebookModel.id == notebook_id)
        )
        result = await session.execute(stmt)
        notebook = result.scalar_one_or_none()

        if notebook:
            sources_metadata = [
                {
                    "id": source.id,
                    "title": source.title,
                    "source_type": source.source_type,
                    "url": source.url,
                }
                for source in notebook.sources
            ]
            notes_data = [
                {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content,
                }
                for note in notebook.notes
            ]

    chunks_data: List[Dict[str, Any]] = []
    if query and query.strip():
        embedder = await get_default_embedding_model()
        query_vector = await embedder.aembed_query(query)
        chunks_data = await vector_store.search(
            query_embedding=query_vector,
            notebook_id=notebook_id,
            limit=top_k_chunks,
        )

    return {
        "notebook_id": notebook_id,
        "sources": sources_metadata,
        "notes": notes_data,
        "chunks": chunks_data,
    }
