Open Notebook Light
Schlanke, performante KI-Research-Engine mit eingebettetem SQLite, ChromaDB und lokalem OpenAI-kompatiblem LLM-Backend (IBM Granite Stack).

1. Systemarchitektur & Tech-Stack
Das Projekt setzt auf eine entkoppelte Monorepo-Architektur:

Frontend: Next.js (App Router, TypeScript, Tailwind CSS, Lucide React)

Backend: FastAPI (Python 3.11+, Uvicorn, Pydantic v2)

Datenbank & Persistenz: * Relationale Daten: SQLite via SQLAlchemy (Async) & Aiosqlite

Vektor-Store: ChromaDB (Persistent Client) mit Kosinus-Metrik

KI & Orchestrierung: LangChain, LangGraph (Checkpointing via SQLite), lokaler llama-server (IBM Granite 4.0 H-Tiny & Embedding-Modell)

2. Projekt-Struktur
Plaintext
open-notebook-light/
├── api/                              # FastAPI-Router & App-Factory
│   ├── main.py                       # Server-Entrypoint & Router-Registrierung
│   └── routers/
│       ├── chat.py                   # RAG-Chat-Endpunkt (ChromaDB + LLM)
│       ├── notebooks.py              # Notizbuch-CRUD-Operationen
│       └── sources.py                # Dokumenten-Upload & Quellen-Verwaltung
│
├── open_notebook/                    # Backend-Core & Business-Logik
│   ├── ai/                           # Modell-Fabrik (models.py)
│   ├── database/                     # SQLite & ChromaDB-Anbindung
│   │   ├── sqlite_client.py          # Asynchroner Session-Manager
│   │   ├── models_sqlite.py          # SQLAlchemy ORM-Modelle
│   │   └── vector_store.py           # ChromaDB Persistent Client Wrapper
│   ├── domain/                       # Pydantic Basis-Modelle
│   ├── graphs/                       # RAG-Pipelines & Ingestion (ask.py, chat.py, source.py)
│   └── utils/                        # PDF-Extractor & Context-Builder
│
├── frontend/                         # Next.js Webinterface (App Router)
│   ├── src/app/                      # Dashboard, Sources, Chat
│   ├── package.json
│   └── .env.local                    # NEXT_PUBLIC_API_URL=http://localhost:8000
│
├── data/                             # Persistenz (in .gitignore)
│   ├── notebook.db                   # SQLite Datenbank
│   └── chroma/                       # ChromaDB Vektor-Store
│
├── pyproject.toml                    # Python-Abhängigkeiten & Build-Manifest
├── start.sh / stop.sh                # Server-Steuerungsskripte
└── .env                              # Lokale Umgebungsvariablen
3. Implementierung & Kernkomponenten
Backend & Ingestion
Dokumenten-Verarbeitung: Unterstützt .pdf, .txt, .md, .html. PDFs werden im Arbeitsspeicher ausgelesen (pypdf), via RecursiveCharacterTextSplitter in Chunks zerlegt und über den lokalen Embedding-Modell-Endpunkt in ChromaDB indiziert.

RAG-Pipeline: Benutzeranfragen werden eingebettet, gegen den ChromaDB-Vektor-Store abgeglichen (Top-K-Chunks) und zusammen mit dem Kontext an das lokale IBM-Granite-Modell übergeben.

Fehlerbehebung: Clientseitige Optimierungen (wie das Bereinigen nicht unterstützter OpenAI-Parametertypen wie repeat_penalty) sichern die Stabilität der LLM-Kommunikation.

Frontend
Vollständig in das FastAPI-Backend integrierte Weboberfläche auf Next.js-Basis.

Dashboard / Notizbücher: Erstellen, Verwalten und Löschen von Forschungsprojekten.

Quellen-Management: Direkter Upload von Dokumenten inklusive Live-Statusanzeige und Vektor-Löschsynchronisation.

RAG-Chat: Interaktives Chat-Interface mit optionaler Notizbuch-Filterung und direkter Quellen-Referenzierung (Chunk-Match-Anzeige).

Dieser Code wurde im Rahmen dieses Projekts aus dem Open-Notebook-Ursprungssystem herausgelöst, modular verschlankt und kann im Rahmen der entsprechenden Open-Source-Lizenzbedingungen frei weiterverwendet werden.
