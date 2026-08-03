"""
Open Notebook Light - Relationale SQLAlchemy ORM Modelle
Modul: open_notebook/database/models_sqlite.py
Zweck: Deklaratives Schema für Notebooks, Sources, Notes und Chat-Sessions
inklusive relationaler Junction-Tabellen als Ersatz für Graph-Kanten.
Version: 2.0.0-light
"""
__version__ = "2.0.0-light"

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def generate_uuid() -> str:
    return uuid.uuid4().hex

class Base(DeclarativeBase):
    pass

notebook_sources = Table(
    "notebook_sources",
    Base.metadata,
    Column("notebook_id", String(32), ForeignKey("notebooks.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", String(32), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)

notebook_notes = Table(
    "notebook_notes",
    Base.metadata,
    Column("notebook_id", String(32), ForeignKey("notebooks.id", ondelete="CASCADE"), primary_key=True),
    Column("note_id", String(32), ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
)

class NotebookModel(Base):
    __tablename__ = "notebooks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    sources: Mapped[List["SourceModel"]] = relationship(
        "SourceModel", secondary=notebook_sources, back_populates="notebooks"
    )
    notes: Mapped[List["NoteModel"]] = relationship(
        "NoteModel", secondary=notebook_notes, back_populates="notebooks"
    )

class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    notebooks: Mapped[List[NotebookModel]] = relationship(
        "NotebookModel", secondary=notebook_sources, back_populates="sources"
    )

class NoteModel(Base):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    notebooks: Mapped[List[NotebookModel]] = relationship(
        "NotebookModel", secondary=notebook_notes, back_populates="notes"
    )

class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_uuid)
    notebook_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), default="Neues Gespräch")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
