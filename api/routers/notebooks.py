"""
Open Notebook Light - Notebooks API Router
Modul: api/routers/notebooks.py
Zweck: Endpunkte zum Erstellen, Auflisten und Löschen von Notizbüchern.
Version: 2.0.0-light
"""

__version__ = "2.0.0-light"

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from loguru import logger

from open_notebook.database.sqlite_client import sqlite_client
from open_notebook.database.models_sqlite import NotebookModel

router = APIRouter()


class NotebookCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None


class NotebookResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    archived: bool
    sources_count: int = 0

    class Config:
        from_attributes = True


@router.post("/", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
async def create_notebook(payload: NotebookCreateRequest):
    """Erstellt ein neues Notizbuch in SQLite."""
    async with sqlite_client.session() as session:
        notebook = NotebookModel(
            title=payload.title,
            description=payload.description,
        )
        session.add(notebook)
        await session.flush()
        logger.info(f"Neues Notizbuch erstellt: {notebook.title} (ID: {notebook.id})")
        return NotebookResponse(
            id=notebook.id,
            title=notebook.title,
            description=notebook.description,
            archived=notebook.archived,
            sources_count=0
        )


@router.get("/", response_model=List[NotebookResponse])
async def list_notebooks():
    """Listet alle nicht-archivierten Notizbücher inkl. Quellen-Anzahl auf."""
    async with sqlite_client.session() as session:
        stmt = (
            select(NotebookModel)
            .options(selectinload(NotebookModel.sources))
            .where(NotebookModel.archived == False)
            .order_by(NotebookModel.created_at.desc())
        )
        result = await session.execute(stmt)
        notebooks = result.scalars().all()

        return [
            NotebookResponse(
                id=nb.id,
                title=nb.title,
                description=nb.description,
                archived=nb.archived,
                sources_count=len(nb.sources)
            )
            for nb in notebooks
        ]


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(notebook_id: str):
    """Löscht ein Notizbuch aus SQLite."""
    async with sqlite_client.session() as session:
        stmt = select(NotebookModel).where(NotebookModel.id == notebook_id)
        result = await session.execute(stmt)
        notebook = result.scalar_one_or_none()

        if not notebook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notizbuch nicht gefunden.")

        await session.delete(notebook)
        logger.info(f"Notizbuch ID {notebook_id} gelöscht.")
        return None
