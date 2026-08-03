# Architecture & Technical Specification (Open Notebook Lite)

## 1. Architektonische Namenskonventionen & Standards

Damit das gesamte Projekt (Backend, Datenbanken, KI-Pipelines und Frontend) einer einheitlichen, wartbaren Struktur folgt, gelten im Repository folgende verbindliche Konventionen:

### Backend (Python / FastAPI)
* **Dateinamen & Module:** `snake_case` (z. B. `sqlite_client.py`, `context_builder.py`).
* **Klassen:** `PascalCase` (z. B. `GraniteModelFactory`, `SourceModel`, `VectorStore`).
* **Funktionen & Methoden:** `snake_case` mit expliziter Typ-Annotation und Asynchronität (`async def execute_rag_vector_search(...) -> List[Dict[str, Any]]:`).
* **Konstanten & Umgebungsvariablen:** `UPPER_SNAKE_CASE` (z. B. `OPENAI_API_BASE`, `CHUNK_SIZE`).
* **Pydantic- & ORM-Modelle:** Endung `Model` bei ORM (`NotebookModel`), Endung `Request`/`Response` bei API-Schemas (`NotebookCreateRequest`, `SourceResponse`).

### Frontend (TypeScript / Next.js)
* **Dateinamen:** React-Komponenten in `snake_case` oder `kebab-case` (z. B. `sidebar.tsx`), Next.js-Seiten strikt als `page.tsx`.
* **Komponenten:** `PascalCase` (z. B. `SidebarNav`, `NotebooksPage`).
* **Funktionen & Variablen:** `camelCase` (z. B. `handleUpload`, `fetchNotebooks`).
* **Interfaces & Typen:** `PascalCase` (z. B. `Notebook`, `SourceUsed`, `Message`).

### REST API-Design
* **Routen-Pfade:** Pluralisierte Ressourcen im Kleinfluss (z. B. `/api/notebooks`, `/api/sources`, `/api/chat`).
* **HTTP-Methoden:**
  * `GET`: Auslesen von Daten (keine Seiteneffekte).
  * `POST`: Erstellen neuer Ressourcen oder Ausführen komplexer Aktionen (z. B. File-Upload, Chat-Anfrage).
  * `DELETE`: Entfernen von Ressourcen (inkl. kaskadierender Bereinigung in SQLite & ChromaDB).

---

## 2. Vollständige Funktions- & Ablauf-Kartierung

### Backend: API-Router Tier (`api/`)

#### `api/main.py` (Server-Entrypoint & Lifespan Manager)
* **`lifespan(app: FastAPI)`**: Steuert Start und Stopp des Servers. Führt beim Start atomar die DDL-Erstellung aller SQLite-Tabellen (`Base.metadata.create_all`) durch und prüft die ChromaDB-Vektorsammlung.
* **`health_check()`** (`GET /health`): Prüft den Systemstatus, die Existenz der SQLite-Datei und die Anzahl indizierter Vektor-Chunks.

#### `api/routers/notebooks.py` (Notizbuch-Verwaltung)
* **`create_notebook`** (`POST /api/notebooks`): Speichert ein neues Notizbuch in der SQLite-Tabelle `notebooks`.
* **`list_notebooks`** (`GET /api/notebooks`): Liest alle aktiven Notizbücher aus und berechnet die Anzahl zugeordneter Quellen.
* **`delete_notebook`** (`DELETE /api/notebooks/{notebook_id}`): Löscht ein Notizbuch atomar aus SQLite (kaskadierend).

#### `api/routers/sources.py` (Dokumenten-Ingestion & Quellen)
* **`list_sources`** (`GET /api/sources`): Liest alle hochgeladenen Dokumente absteigend nach Erstellungsdatum aus SQLite aus.
* **`upload_source`** (`POST /api/sources/upload`): Strikte MIME-Type-Validierung. Speichert Datensatz in SQLite mit Status `processing` und übergibt das Chunking asynchron an `background_tasks`.
* **`get_source`** (`GET /api/sources/{source_id}`): Liefert Metadaten einer einzelnen Quelle.
* **`delete_source`** (`DELETE /api/sources/{source_id}`): Löscht den Eintragsdatensatz aus SQLite **und** entfernt gleichzeitig alle zugehörigen Vektor-Chunks aus ChromaDB.

#### `api/routers/chat.py` (RAG KI-Interface)
* **`execute_chat`** (`POST /api/chat`): Startet die RAG-Pipeline: Generiert Abfrage-Embedding, führt Kosinus-Vektorsuche in ChromaDB aus, baut System-Prompt mit Kontext auf und ruft IBM Granite 4.0 H-Tiny auf.

---

### Backend: Core & KI-Orchestrierung (`open_notebook/`)

#### `open_notebook/ai/models.py` (Modell-Fabrik)
* **`GraniteModelFactory.get_chat_model()`**: Baut die `ChatOpenAI`-Instanz von LangChain auf (IBM Granite 4.0 H-Tiny).
* **`GraniteModelFactory.get_embedding_model()`**: Baut die `OpenAIEmbeddings`-Instanz auf (Granite Embedding 107M Multilingual).

#### `open_notebook/database/` (Persistenzschicht)
* **`SQLiteClient.session()`** (`sqlite_client.py`): Asynchroner Kontextmanager für SQLAlchemy-Sessions mit aktivierten WAL-Pragmas (`PRAGMA journal_mode=WAL`).
* **`VectorStore`** (`vector_store.py`):
  * `add_chunks()`: Schreibt Chunks und 384-dim Vektoren in ChromaDB.
  * `search()`: Führt Kosinus-Ähnlichkeitssuche durch.
  * `delete_source_chunks()`: Entfernt Vektoren einer gelöschten Quelle aus ChromaDB.

#### `open_notebook/graphs/` & `open_notebook/utils/` (Pipelines & Utilities)
* **`extract_text_from_pdf_bytes()`** (`pdf_extractor.py`): In-Memory-Stream-Reader via `pypdf`.
* **`chunk_and_embed_node()`** (`graphs/source.py`): Zerschneidet Text in 400-Token-Chunks (50 Overlap), berechnet Embeddings, speichert sie in ChromaDB und setzt den Status in SQLite auf `completed`.
* **`execute_rag_vector_search()`** (`graphs/ask.py`): Betbettet Anfragetext ein und führt Vektorsuche in ChromaDB aus.
* **`build_context_for_chat()`** (`utils/context_builder.py`): Liest relationale Metadaten und kombiniert sie mit Vektor-Chunks zu einem konsolidierten Prompt-Payload.

---

## 3. Übersichtstabelle API-Endpunkte

| HTTP-Methode | Pfad | Parameter / Payload | Aufgerufene Backend-Komponenten | Ziel / Auswirkung |
| --- | --- | --- | --- | --- |
| **GET** | `/health` | Keine | `sqlite_client`, `vector_store` | Liefert Systemstatus, DB-Pfad und Vektor-Anzahl. |
| **GET** | `/api/notebooks` | Keine | `sqlite_client.session` -> `NotebookModel` | Liest Notizbücher mit Quellenanzahl. |
| **POST** | `/api/notebooks` | `{ "title": str, "description": str }` | `sqlite_client.session` -> `NotebookModel` | Erstellt neues Notizbuch. |
| **DELETE** | `/api/notebooks/{id}` | Path Parameter: `id` | `sqlite_client.session` -> `NotebookModel` | Löscht Notizbuch. |
| **GET** | `/api/sources` | Keine | `sqlite_client.session` -> `SourceModel` | Liest alle Dokumente aus. |
| **POST** | `/api/sources/upload` | Form Data: `file`, `notebook_id` | `pdf_extractor`, `SourceModel`, `chunk_and_embed_node` | Validiert, extrahiert Text, startet Indizierung. |
| **DELETE** | `/api/sources/{id}` | Path Parameter: `id` | `SourceModel`, `vector_store.delete_source_chunks` | Löscht Dokument und Vektoren. |
| **POST** | `/api/chat` | `{ "message": str, "notebook_id": str }` | `execute_rag_vector_search`, `GraniteModelFactory` | Führt RAG-Suche aus und generiert Antwort. |

---

## 4. End-to-End Daten- & Aufrufflüsse

### Ablauf A: Dokumenten-Ingestion (Upload & Indexierung)
1. **User-Aktion:** Nutzer lädt PDF im Frontend hoch (`sources/page.tsx`).
2. **API-Boundary:** Request auf `POST /api/sources/upload`.
3. **Validierung & Extraktion:** MIME-Prüfung und Text-Extraktion im Arbeitsspeicher (`pypdf`).
4. **Relationales Staging:** Datensatz in SQLite (`sources`-Tabelle) mit Status `processing`.
5. **Asynchroner Worker:** `chunk_and_embed_node()` zerlegt in 400-Token-Chunks, bettet über Granite 107M ein, speichert in ChromaDB und aktualisiert Status in SQLite auf `completed`.

### Ablauf B: RAG-Chat & Antwortgenerierung
1. **User-Aktion:** Frage im Chat (`chat/page.tsx`).
2. **API-Call:** Request auf `POST /api/chat`.
3. **Vektor-Retrieval:** `execute_rag_vector_search()` sucht Top-Chunks in ChromaDB via Kosinus-Distanz.
4. **Kontext-Assemblierung:** Passagen werden in den `SYSTEM_PROMPT` injiziert.
5. **LLM-Synthese:** Anfrage an IBM Granite 4.0 H-Tiny via TurboQuant-Router.
6. **Response-Delivery:** Generierte Antwort inkl. Quellennachweisen geht ans Frontend.
