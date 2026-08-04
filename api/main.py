"""
Open Notebook Light - Hauptanwendungs-Factory (Phase 2 Update)
Modul: api/main.py
Version: 2.1.0-light
"""

__version__ = "2.1.0-light"

from dotenv import load_dotenv
load_dotenv()  # Muss vor allen anderen Projekt-Imports stehen

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from open_notebook.database.sqlite_client import sqlite_client
from open_notebook.database.models_sqlite import Base
from open_notebook.database.vector_store import vector_store
from api.routers import sources, notebooks, chat, search, settings, logs

# Zentrale rotierende Log-Datei konfigurieren
log_path = os.getenv("LOG_FILE_PATH", "/app/data/logs/open_notebook.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logger.add(log_path, rotation="10 MB", retention="14 days", compression="zip", enqueue=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Open Notebook Light v2.1.0-light startet ===")
    async with sqlite_client.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    chunk_count = vector_store.collection.count()
    logger.info(f"ChromaDB Vektor-Store bereit. Aktuelle Chunks in Sammlung: {chunk_count}")
    yield
    logger.info("=== Open Notebook Light wird heruntergefahren ===")


app = FastAPI(
    title="Open Notebook Light API",
    description="Schlanke KI-Research-Engine mit SQLite und ChromaDB (IBM Granite Stack)",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Alle 6 Core Router registrieren
app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(notebooks.router, prefix="/api/notebooks", tags=["Notebooks"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])


@app.get("/health", tags=["Health"])
async def health_check():
    sqlite_db_path = os.getenv("SQLITE_DB_PATH", "/app/data/notebook.db")
    chroma_db_path = os.getenv("CHROMA_DB_PATH", "/app/data/chroma")
    return {
        "status": "healthy",
        "version": __version__,
        "architecture": "Open Notebook Light (SQLite + ChromaDB + IBM Granite)",
        "persistence": {
            "sqlite_db": sqlite_db_path,
            "sqlite_exists": os.path.exists(sqlite_db_path),
            "chroma_path": chroma_db_path,
            "vector_chunks": vector_store.collection.count(),
        }
    }
