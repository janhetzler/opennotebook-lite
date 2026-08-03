"""
Open Notebook Light - Chat-Orchestrierungsgraph
Modul: open_notebook/graphs/chat.py
Zweck: Verwaltung des mehrstufigen KI-Dialogs unter Nutzung von langgraph-checkpoint-sqlite.
Version: 2.0.0-light
"""
__version__ = "2.0.0-light"

import os
from typing import Any, Dict
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from open_notebook.utils.context_builder import build_context_for_chat

DB_PATH = os.getenv("SQLITE_DB_PATH", "/app/data/notebook.db")

async def get_chat_checkpointer() -> AsyncSqliteSaver:
    conn = await aiosqlite.connect(DB_PATH)
    return AsyncSqliteSaver(conn)

async def prepare_chat_step(state: Dict[str, Any]) -> Dict[str, Any]:
    notebook_id = state["notebook_id"]
    user_message = state["user_message"]

    context = await build_context_for_chat(
        notebook_id=notebook_id,
        query=user_message,
    )

    return {
        "context": context,
        "messages": state.get("messages", []) + [{"role": "user", "content": user_message}],
    }
