"""
Open Notebook Light - Asynchroner SQLite Session-Manager
Modul: open_notebook/database/sqlite_client.py
Zweck: Bietet eine asynchrone SQLAlchemy-Verbindung mit Write-Ahead-Logging (WAL-Modus)
und erzwungener Fremdschlüssel-Prüfung.
Version: 2.0.0-light
"""
__version__ = "2.0.0-light"

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import engine
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DB_PATH = os.getenv("SQLITE_DB_PATH", "/app/data/notebook.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

class SQLiteClient:
    def __init__(self, db_url: str = DATABASE_URL):
        self.engine: AsyncEngine = create_async_engine(
            db_url,
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        self._register_events()

    def _register_events(self) -> None:
        @listens_for(engine.Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.close()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

sqlite_client = SQLiteClient()
