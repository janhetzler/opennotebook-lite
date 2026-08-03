"""
Open Notebook Light - Dokumenten-Ingestion Pipeline
Modul: open_notebook/graphs/source.py
Zweck: Text-Chunking (400 Tokens / 50 Overlap), Vektor-Generierung und Datenbank-Update.
Version: 2.0.0-light
"""
__version__ = "2.0.0-light"

import os
from typing import Any, Dict, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import update
from loguru import logger

from open_notebook.ai.models import get_default_embedding_model
from open_notebook.database.sqlite_client import sqlite_client
from open_notebook.database.models_sqlite import SourceModel
from open_notebook.database.vector_store import vector_store

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

async def chunk_and_embed_node(state: Dict[str, Any]) -> Dict[str, Any]:
    source_id: str = state["source_id"]
    notebook_ids: List[str] = state.get("notebook_ids", [])
    full_text: str = state.get("full_text", "")

    if not full_text or not full_text.strip():
        logger.warning(f"Source ID {source_id} enthält keinen digitalen Text. Ingestion abgebrochen.")
        async with sqlite_client.session() as session:
            stmt = (
                update(SourceModel)
                .where(SourceModel.id == source_id)
                .values(processing_status="failed_no_digital_text")
            )
            await session.execute(stmt)
        return {"source_id": source_id, "status": "failed", "chunks_count": 0}

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_text(full_text)

    if not chunks:
        return {"source_id": source_id, "status": "completed", "chunks_count": 0}

    embedder = await get_default_embedding_model()
    embeddings = await embedder.aembed_documents(chunks)

    await vector_store.add_chunks(
        source_id=source_id,
        notebook_ids=notebook_ids,
        chunks=chunks,
        embeddings=embeddings,
    )

    async with sqlite_client.session() as session:
        stmt = (
            update(SourceModel)
            .where(SourceModel.id == source_id)
            .values(processing_status="completed")
        )
        await session.execute(stmt)

    logger.info(f"Ingestion für Source ID {source_id} erfolgreich abgeschlossen ({len(chunks)} Chunks).")
    return {
        "source_id": source_id,
        "status": "completed",
        "chunks_count": len(chunks),
    }
