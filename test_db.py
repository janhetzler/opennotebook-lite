import asyncio
from dotenv import load_dotenv

# Lade Umgebungsvariablen für Standalone-Testlauf
load_dotenv()

from open_notebook.graphs.ask import execute_rag_vector_search
from open_notebook.database.sqlite_client import sqlite_client
from sqlalchemy import select
from open_notebook.database.models_sqlite import SourceModel

async def test():
    # 1. SQLite abfragen
    async with sqlite_client.session() as session:
        result = await session.execute(select(SourceModel))
        sources = result.scalars().all()
        print('--- SQLite Eintraege ---')
        for s in sources:
            print(f'ID: {s.id} | Title: {s.title} | Status: {s.processing_status}')
            
    # 2. ChromaDB abfragen
    print('\n--- ChromaDB RAG-Suche ---')
    results = await execute_rag_vector_search(
        query='lokale Vektorspeicher',
        notebook_id='', 
        top_k=2
    )
    for r in results:
        print(f'Distance: {r["distance"]:.4f} | Text: {r["text"]}')

asyncio.run(test())
