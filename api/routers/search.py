"""
Open Notebook Light - Search API Router
Modul: api/routers/search.py
Zweck: Endpunkt für die globale semantische Vektorsuche in ChromaDB.
Version: 2.1.0-light
"""

__version__ = "2.1.0-light"

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from loguru import logger

from open_notebook.graphs.ask import execute_rag_vector_search

router = APIRouter()


class SearchResultItem(BaseModel):
    chunk_id: str
    source_id: str
    text: str
    score: float
    distance: float


class SearchResponse(BaseModel):
    query: str
    results_count: int
    results: List[SearchResultItem]


@router.get("", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=1, description="Suchbegriff für die semantische Vektorsuche"),
    notebook_id: Optional[str] = Query(None, description="Optionaler Notizbuch-Filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximale Anzahl an Treffern")
):
    """Führt eine Kosinus-Ähnlichkeitssuche über alle indizierten ChromaDB-Chunks durch."""
    if not q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Der Suchbegriff darf nicht leer sein.")

    logger.info(f"Globale Vektorsuche gestartet: '{q}' (Notebook-ID: {notebook_id}, Limit: {limit})")

    raw_results = await execute_rag_vector_search(
        query=q,
        notebook_id=notebook_id or "",
        top_k=limit
    )

    formatted_results = [
        SearchResultItem(
            chunk_id=r.get("chunk_id", r.get("source_id", "unknown")),
            source_id=r.get("source_id", "unknown"),
            text=r.get("text", r.get("content", "")),
            score=round(1.0 - r.get("distance", 0.0), 4),
            distance=round(r.get("distance", 0.0), 4)
        )
        for r in raw_results
    ]

    return SearchResponse(
        query=q,
        results_count=len(formatted_results),
        results=formatted_results
    )
