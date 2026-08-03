import asyncio
from dotenv import load_dotenv
load_dotenv()

from open_notebook.database.sqlite_client import sqlite_client
from open_notebook.graphs.chat import get_chat_checkpointer, prepare_chat_step
from open_notebook.ai.models import get_default_chat_model
from open_notebook.database.models_sqlite import ChatSessionModel, NotebookModel
from sqlalchemy import select

async def run_multi_turn_test():
    # 1. Wir legen ein Test-Notebook und eine Test-Session in SQLite an
    notebook_id = "test_notebook_uuid"
    session_id = "test_session_uuid"
    
    # 1. Wir legen ein Test-Notebook in SQLite an
    notebook_id = "test_notebook_uuid"
    session_id = "test_session_uuid"
    
    async with sqlite_client.session() as session:
        nb_check = await session.execute(select(NotebookModel).where(NotebookModel.id == notebook_id))
        if not nb_check.scalar_one_or_none():
            db_nb = NotebookModel(id=notebook_id, title="Test Notebook")
            session.add(db_nb)
            await session.commit()
            
    # 2. Session anlegen
    async with sqlite_client.session() as session:
        sess_check = await session.execute(select(ChatSessionModel).where(ChatSessionModel.id == session_id))
        if not sess_check.scalar_one_or_none():
            db_sess = ChatSessionModel(id=session_id, notebook_id=notebook_id, title="Multi-Turn Chat Test")
            session.add(db_sess)
            await session.commit()
            
    print("=== SQLite Test-Session & Notebook initialisiert ===")

    # 2. Checkpointer initialisieren
    checkpointer = await get_chat_checkpointer()
    config = {"configurable": {"thread_id": session_id}}

    # 3. Erste Nachricht
    state_turn1 = {
        "notebook_id": notebook_id,
        "user_message": "Hallo Granite. Nenne mir bitte die Zahl 42.",
        "messages": []
    }
    
    # Zustand vorbereiten (Kontext bauen)
    step1 = await prepare_chat_step(state_turn1)
    
    # LLM-Aufruf
    llm = await get_default_chat_model()
    response1 = await llm.ainvoke(step1["messages"])
    print(f"User: {state_turn1['user_message']}")
    print(f"Granite Response: {response1.content}")
    
    # Zustand im Checkpointer persistent speichern
    new_messages = step1["messages"] + [{"role": "assistant", "content": response1.content}]
    await checkpointer.aput(
        config=config,
        checkpoint={"v": 1, "ts": "2026-08-03T00:00:00Z", "id": "cp1", "channel_values": {"messages": new_messages}},
        metadata={"source": "api"}
    )
    
    # 4. Zweite Nachricht (Multi-Turn Test: Modell muss sich an die Zahl 42 erinnern)
    state_turn2 = {
        "notebook_id": notebook_id,
        "user_message": "Welche Zahl habe ich dir gerade genannt?",
        "messages": new_messages
    }
    
    step2 = await prepare_chat_step(state_turn2)
    response2 = await llm.ainvoke(step2["messages"])
    print(f"\nUser: {state_turn2['user_message']}")
    print(f"Granite Response: {response2.content}")
    
    # 5. Persistente Checkpoint-Speicherung verifizieren
    saved_checkpoint = await checkpointer.aget(config)
    print("\n=== Checkpoint Persistenz Verifikation ===")
    if saved_checkpoint:
        history = saved_checkpoint["channel_values"].get("messages", [])
        print(f"Erfolgreich geladen aus SQLite Checkpointer. Anzahl Nachrichten im Verlauf: {len(history)}")
        for idx, msg in enumerate(history):
            if isinstance(msg, dict):
                role = "User" if msg.get("role") == "user" else "Granite"
                content = msg.get("content")
            else:
                role = "User" if getattr(msg, "type", "") == "human" else "Granite"
                content = msg.content
            print(f"  [{idx}] {role}: {content}")
    else:
        print("Fehler: Konnte keinen Checkpoint laden!")

asyncio.run(run_multi_turn_test())
