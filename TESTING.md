# Test- und Abdeckungsstrategie: Open Notebook Light

## 1. Identifikation kritischer Pfade (Risk-Based Testing)
Folgende Prozesse sind das Herzstück der Anwendung und müssen priorisiert abgesichert werden:

* **Atomarität der Löschvorgänge (Sync-Check):** Wenn eine Quelle in SQLite gelöscht wird, müssen die Chunks in ChromaDB ebenfalls verschwinden. Verwaiste Vektoren führen zu Halluzinationen.
* **Ingestion-Pipeline (Asynchronität):** Der Übergang von `UploadFile` -> `pypdf` -> `RecursiveCharacterTextSplitter` -> `ChromaDB` ist fehleranfällig (z. B. leere PDFs, Sonderzeichen).
* **RAG-Kontext-Integrität:** Stellt sicher, dass `build_context_for_chat` nur Daten aus dem gewählten `notebook_id` zieht (Mandantentrennung auf Logik-Ebene).
* **LLM-Fehlertoleranz:** Korrektes Handling von Timeouts oder "Garbage-Output" des lokalen LLM-Routers.

## 2. Empfohlene Unit-Tests (Modultests)
Unit-Tests sollten ohne externe Abhängigkeiten (kein echtes LLM, keine echte DB) laufen.

### Backend (Python/Pytest)
* **`open_notebook.utils.pdf_extractor`:**
  * Test mit validem Text-PDF.
  * Test mit korruptem PDF (Erwartung: `ValueError`).
  * Test mit leerem/Bild-basiertem PDF (Erwartung: leerer String).
* **`open_notebook.graphs.source` (Chunking-Logik):**
  * Prüfen, ob der `RecursiveCharacterTextSplitter` die Chunks korrekt gemäß `CHUNK_SIZE` schneidet.
  * Prüfen der Überlappung (`CHUNK_OVERLAP`).
* **Pydantic Modelle:**
  * Validierung der `ChatRequest`- und `NotebookCreateRequest`-Schemas.

### Frontend (Jest/Vitest)
* **Formatierung:** Prüfung, ob der Match-Score (Kosinus-Distanz) korrekt in Prozent umgerechnet wird.
* **Status-Badges:** Korrekte Farbdarstellung für `processing`, `completed`, `failed`.

## 3. Empfohlene Integrationstests
Hier testen wir das Zusammenspiel der Komponenten mit einer Test-Datenbank.

* **API -> SQLite:**
  `POST /api/notebooks` erstellt Eintrag und `GET /api/notebooks` gibt ihn inkl. UUID zurück.
* **API -> Background Task:**
  Mocking der Embedding-Funktion, um zu prüfen, ob der Status einer Quelle von `processing` auf `completed` wechselt.
* **Vector Search:**
  Einbetten von Test-Daten in eine temporäre ChromaDB-Kollektion und Verifikation, dass `execute_rag_vector_search` bei einer gezielten Abfrage das richtige Dokument zurückgibt.
* **Multi-Turn Chat (Checkpointer):**
  Verifikation, dass `langgraph-checkpoint-sqlite` den Verlauf speichert (ähnlich wie in `test_chat.py`).

## 4. Beispielhafter Test-Boilerplate-Code
Um eine hohe Abdeckung zu erreichen, sollte `pytest-asyncio` verwendet werden. Wir nutzen `httpx.AsyncClient` für die API-Tests und `unittest.mock` für das LLM.

### A. Backend Integration Test (`tests/test_api_sources.py`)
```python
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from api.main import app

@pytest.mark.asyncio
async def test_upload_pdf_flow():
    """Testet den gesamten Flow vom Upload bis zur Hintergrund-Task-Übergabe."""
    
    # Mocking der PDF-Extraktion und der Embedding-Modelle
    with patch("api.routers.sources.extract_text_from_pdf_bytes") as mock_pdf, \
         patch("open_notebook.graphs.source.get_default_embedding_model") as mock_embed:
        
        mock_pdf.return_value = "Das ist ein Test-Text aus dem PDF."
        
        # Mocking des Embedders
        mock_embed_instance = MagicMock()
        mock_embed_instance.aembed_documents.return_value = [[0.1] * 384] # Fake Embedding
        mock_embed.return_value = mock_embed_instance

        async with AsyncClient(app=app, base_url="http://test") as ac:
            # 1. Datei hochladen
            files = {'file': ('test.pdf', b'fake-pdf-content', 'application/pdf')}
            response = await ac.post("/api/sources/upload", files=files)
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "test.pdf"
            assert data["processing_status"] == "processing"
            
            source_id = data["id"]

            # 2. Status in DB prüfen (müsste nach einiger Zeit 'completed' sein)
```

### B. Unit Test für Context Builder (`tests/test_context_builder.py`)
```python
import pytest
from open_notebook.utils.context_builder import build_context_for_chat

@pytest.mark.asyncio
async def test_build_context_empty_db():
    """Verstellt sicher, dass der Context-Builder bei unbekannter ID nicht abstürzt."""
    context = await build_context_for_chat(notebook_id="non-existent")
    
    assert context["notebook_id"] == "non-existent"
    assert len(context["sources"]) == 0
    assert len(context["chunks"]) == 0
```

## 5. RAG Evaluation (Die "KI-Teststrategie")
Da es sich um ein RAG-System handelt, reicht Code-Abdeckung nicht aus. Die Qualität der Antworten muss gemessen werden:

* **Retrieval Test (Gold Standard):** Erstelle 10 Test-Dokumente und 10 spezifische Fragen. Prüfe, ob die richtigen Chunks unter den Top-4 landen.
* **Faithfulness Test:** Prüfe (manuell oder via LLM-as-a-judge), ob das Modell in `api/routers/chat.py` wirklich nur den Kontext nutzt oder zu halluzinieren beginnt, wenn "Keine relevanten Passagen gefunden" übergeben wird.
* **Boundary Test:** Was passiert, wenn der Kontext 8000 Tokens überschreitet? (Context Window Management).

## 6. Zusammenfassung der Testabdeckung

| Komponente | Test-Art | Ziel-Abdeckung | Tool |
| --- | --- | --- | --- |
| API Endpunkte | Integration | > 90% | Pytest + HTTPX |
| PDF Extraction | Unit | 100% | Pytest |
| Vector Store Ops | Integration | > 80% | Pytest + Chroma Ephemeral |
| SQLite Schema | Migration Test | 100% | Alembic / SQLAlchemy |
| Frontend UI | E2E / Component | > 60% | Playwright / Vitest |
| KI-Antworten | Evaluation | N/A | RAGAS / Manuell |

**Empfehlung:** Starte mit der Absicherung der `delete_source`-Logik, da laut `ARCHITECTURE.md` die Konsistenz zwischen SQLite und ChromaDB manuell programmiert wurde und dort das höchste Risiko für Datenleichen besteht.
