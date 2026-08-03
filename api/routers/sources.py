"""
Open Notebook Light - Sources API Router (Aktualisiert)
Modul: api/routers/sources.py
Zweck: Endpunkte für Dokumenten-Upload, Auflistung und Löschung.
Version: 2.0.1-light
"""

__version__ = "2.0.1-light"

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy import select
from loguru import logger

from open_notebook.database.sqlite_client import sqlite_client
from open_notebook.database.models_sqlite import SourceModel, notebook_sources
from open_notebook.database.vector_store import vector_store
from open_notebook.graphs.source import chunk_and_embed_node
from open_notebook.utils.pdf_extractor import extract_text_from_pdf_bytes

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/html",
    "application/json",
}

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown", ".html", ".htm", ".json"}


class SourceResponse(BaseModel):
    id: str
    title: str
    source_type: str
    processing_status: str
    url: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SourceResponse])
async def list_sources():
    """Listet alle hochgeladenen Quellen auf."""
    async with sqlite_client.session() as session:
        stmt = select(SourceModel).order_by(SourceModel.created_at.desc())
        result = await session.execute(stmt)
        sources = result.scalars().all()
        return sources


@router.post("/upload", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_source(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    notebook_id: Optional[str] = Form(None)
):
    """Verarbeitet den Datei-Upload mit MIME-Type-Validierung."""
    filename = file.filename or "unnamed_document"
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""

    if file.content_type not in ALLOWED_MIME_TYPES and ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Upload abgelehnt: Ungültiger MIME-Type '{file.content_type}' ({filename})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ungültiges Dateiformat. Es werden nur digitale Textdokumente unterstützt.",
        )

    content_bytes = await file.read()
    if len(content_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Die Datei ist leer.")

    extracted_text = ""
    if file.content_type == "application/pdf" or ext == ".pdf":
        try:
            extracted_text = extract_text_from_pdf_bytes(content_bytes)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    else:
        extracted_text = content_bytes.decode("utf-8", errors="ignore")

    async with sqlite_client.session() as session:
        new_source = SourceModel(
            title=filename,
            source_type=ext.replace(".", "") or "text",
            full_text=extracted_text,
            processing_status="processing" if extracted_text.strip() else "failed_no_digital_text",
        )
        session.add(new_source)
        await session.flush()

        notebook_ids = []
        if notebook_id:
            notebook_ids.append(notebook_id)
            stmt = notebook_sources.insert().values(notebook_id=notebook_id, source_id=new_source.id)
            await session.execute(stmt)

        source_id = new_source.id

    if extracted_text.strip():
        background_tasks.add_task(
            chunk_and_embed_node,
            {
                "source_id": source_id,
                "notebook_ids": notebook_ids,
                "full_text": extracted_text,
            }
        )

    return new_source


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(source_id: str):
    async with sqlite_client.session() as session:
        stmt = select(SourceModel).where(SourceModel.id == source_id)
        result = await session.execute(stmt)
        source = result.scalar_one_or_none()
        if not source:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quelle nicht gefunden.")
        return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: str):
    async with sqlite_client.session() as session:
        stmt = select(SourceModel).where(SourceModel.id == source_id)
        result = await session.execute(stmt)
        source = result.scalar_one_or_none()
        if not source:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quelle nicht gefunden.")
        await session.delete(source)

    await vector_store.delete_source_chunks(source_id)
    return None
