"""
Open Notebook Light - Settings & Health API Router
Modul: api/routers/settings.py
Zweck: Endpunkt zur Abfrage von Systemkonfigurationen, Pfaden und Router-Verbindungsstatus.
Version: 2.1.0-light
"""

__version__ = "2.1.0-light"

import os
import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger

from open_notebook.database.vector_store import vector_store

router = APIRouter()


class SettingsResponse(BaseModel):
    environment: str
    version: str
    openai_api_base: str
    llm_model_name: str
    embedding_model_name: str
    embedding_dimensions: int
    llm_context_window: int
    chunk_size: int
    chunk_overlap: int
    sqlite_db_path: str
    chroma_db_path: str
    total_vector_chunks: int
    llm_router_online: bool


@router.get("/", response_model=SettingsResponse)
async def get_settings():
    """Liest Umgebungsvariablen aus und prüft per HTTP-Ping die Erreichbarkeit des lokalen LLM-Routers."""
    api_base = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
    llm_online = False

    # Verbindungsprüfung zum lokalen llama-server / TurboQuant Router
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            test_url = f"{api_base.rstrip('/')}/models"
            resp = await client.get(test_url)
            if resp.status_code == 200:
                llm_online = True
    except Exception as e:
        logger.warning(f"LLM-Router Ping fehlgeschlagen ({api_base}): {str(e)}")

    return SettingsResponse(
        environment=os.getenv("ENVIRONMENT", "production"),
        version="2.1.0-light",
        openai_api_base=api_base,
        llm_model_name=os.getenv("LLM_MODEL_NAME", "granite-4.0-h-tiny-UD-Q4_K_XL.gguf"),
        embedding_model_name=os.getenv("EMBEDDING_MODEL_NAME", "granite-embedding-107m-multilingual-Q8_0.gguf"),
        embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "384")),
        llm_context_window=int(os.getenv("LLM_CONTEXT_WINDOW", "8192")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "400")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
        sqlite_db_path=os.getenv("SQLITE_DB_PATH", "/app/data/notebook.db"),
        chroma_db_path=os.getenv("CHROMA_DB_PATH", "/app/data/chroma"),
        total_vector_chunks=vector_store.collection.count(),
        llm_router_online=llm_online,
    )
