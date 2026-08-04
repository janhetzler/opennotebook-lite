"""
Open Notebook Light - ChromaDB Vektor-Store Manager
Modul: open_notebook/database/vector_store.py
Zweck: Verwaltung der persistenten ChromaDB-Kollektion fuer Source-Chunks.
       Bietet Add-, Search- und Delete-Operationen auf Basis von
       vorberechneten Embeddings (keine eigene Modell-Initialisierung hier).
Version: 2.0.0-light
Erstellt: 2026-08-02
"""
__version__ = "2.0.0-light"

import os
from typing import Any, Dict, List

import chromadb
from loguru import logger

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "/app/data/chroma")
COLLECTION_NAME = "source_chunks"


class VectorStore:
    """
    Wrapper um ChromaDB PersistentClient fuer die source_chunks-Kollektion.
    Alle schreibenden und lesenden Operationen gehen ueber diese Klasse.
    Embeddings werden immer von aussen (models.py) berechnet und hier nur gespeichert.
    """

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"ChromaDB VectorStore initialisiert — "
            f"Collection: '{COLLECTION_NAME}', Pfad: {CHROMA_DB_PATH}"
        )

    async def add_chunks(
        self,
        source_id: str,
        notebook_ids: List[str],
        chunks: List[str],
        embeddings: List[List[float]],
    ) -> None:
        """
        Fuegt Text-Chunks mit vorberechneten Embeddings in ChromaDB ein.

        IDs werden als '{source_id}_{chunk_index}' konstruiert, damit
        ein erneutes Einlesen derselben Source idempotent ueberschreibbar ist.
        notebook_ids werden als kommaseparierter String gespeichert
        (ChromaDB unterstuetzt keine Metadaten-Arrays).
        """
        if not chunks or not embeddings:
            logger.warning(f"add_chunks: Keine Daten fuer Source '{source_id}' — Abbruch.")
            return

        ids = [f"{source_id}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source_id": source_id,
                "notebook_ids": ",".join(notebook_ids) if notebook_ids else "",
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        logger.debug(
            f"VectorStore: {len(chunks)} Chunks fuer Source '{source_id}' gespeichert."
        )

    async def search(
        self,
        query_embedding: List[float],
        notebook_id: str,
        limit: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Fuehrt eine Kosinus-Aehnlichkeitssuche durch, gefiltert nach notebook_id.

        Gibt eine geordnete Liste von Dicts zurueck:
        [{"text": ..., "source_id": ..., "chunk_index": ..., "distance": ...}]
        Niedrigerer Distance-Wert = hoehere Aehnlichkeit (Kosinus-Metrik).
        """
        total = self.collection.count()
        if total == 0:
            return []

        n_results = 100 if notebook_id else min(limit, total)
        # ChromaDB unterstuetzt keinen $contains-Operator fuer String-Felder.
        # notebook_ids wird als kommaseparierter String gespeichert, daher
        # suchen wir global (kein Filter) und lassen die Anwendungsschicht filtern.
        where_filter = None

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.warning(f"VectorStore-Suche fehlgeschlagen (notebook_id={notebook_id}): {exc}")
            return []

        output: List[Dict[str, Any]] = []
        if results and results.get("documents"):
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                if notebook_id:
                    n_ids_str = meta.get("notebook_ids", "")
                    if not n_ids_str or notebook_id not in n_ids_str.split(","):
                        continue
                        
                output.append(
                    {
                        "text": doc,
                        "source_id": meta.get("source_id", ""),
                        "chunk_index": meta.get("chunk_index", 0),
                        "distance": dist,
                    }
                )
                if len(output) >= limit:
                    break
        return output

    async def delete_source_chunks(self, source_id: str) -> None:
        """
        Loescht alle Chunks einer bestimmten Source aus ChromaDB.
        Wird beim DELETE /api/sources/{source_id} aufgerufen,
        damit SQLite und ChromaDB synchron bleiben.
        """
        try:
            self.collection.delete(where={"source_id": source_id})
            logger.info(f"VectorStore: Alle Chunks fuer Source '{source_id}' geloescht.")
        except Exception as exc:
            logger.warning(
                f"VectorStore: Fehler beim Loeschen von Source '{source_id}': {exc}"
            )


# Modul-Level Singleton — wird beim Import einmalig initialisiert
vector_store = VectorStore()
