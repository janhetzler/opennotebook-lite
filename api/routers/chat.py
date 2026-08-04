"""
Open Notebook Light - Chat API Router
Modul: api/routers/chat.py
Zweck: Endpunkt für den RAG-basierten KI-Chat mit IBM Granite 4.0 H-Tiny.
Version: 2.0.0-light
"""

__version__ = "2.0.0-light"

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger

import os
from open_notebook.ai.models import get_default_chat_model
from open_notebook.graphs.ask import execute_rag_vector_search

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    notebook_id: Optional[str] = None


class SourceUsed(BaseModel):
    chunk_id: str
    content: str
    score: float


class ChatResponse(BaseModel):
    response: str
    sources_used: List[SourceUsed]


SYSTEM_PROMPT = """Du bist ein präziser Forschungsassistent. 
Beantworte die Frage des Benutzers AUSSCHLIESSLICH auf Basis des folgenden Kontextes. 
Wenn die Information nicht im Kontext enthalten ist, antworte ehrlich, dass du es anhand der vorliegenden Dokumente nicht beantworten kannst.

KONTEXT:
{context}
"""


@router.post("/", response_model=ChatResponse)
async def execute_chat(payload: ChatRequest):
    """Führt eine RAG-Abfrage durch und generiert eine Antwort via Granite 4.0 H-Tiny."""
    if not payload.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Die Nachricht darf nicht leer sein.")

    logger.info(f"RAG-Chat Anfrage empfangen: '{payload.message}' (Notebook ID: {payload.notebook_id})")

    max_dist = float(os.getenv("RAG_MAX_DISTANCE", "1.0"))
    
    retrieved_chunks = await execute_rag_vector_search(
        query=payload.message,
        notebook_id=payload.notebook_id or "",
        top_k=4,
        max_distance=max_dist
    )

    context_text = "\n\n---\n\n".join([c["text"] for c in retrieved_chunks]) if retrieved_chunks else "Keine relevanten Dokumenten-Passagen gefunden."
    formatted_system_prompt = SYSTEM_PROMPT.format(context=context_text)

    chat_llm = await get_default_chat_model()
    messages = [
        SystemMessage(content=formatted_system_prompt),
        HumanMessage(content=payload.message),
    ]

    try:
        llm_response = await chat_llm.ainvoke(messages)
        answer_text = llm_response.content
    except Exception as e:
        logger.error(f"Fehler bei der Kommunikation mit dem LLM-Router: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LLM-Fehler: {str(e)}")

    sources_used = [
        SourceUsed(
            chunk_id=c["source_id"],
            content=c["text"],
            score=round(1.0 - c["distance"], 4)  # Kosinus-Distanz -> Ähnlichkeits-Score
        )
        for c in retrieved_chunks
    ]

    return ChatResponse(
        response=answer_text,
        sources_used=sources_used
    )
