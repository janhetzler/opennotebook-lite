# Open Notebook Light

Open Notebook Light ist eine schlanke, performante und vollständig lokale KI-Research-Engine. Sie ermöglicht es Forschern und Entwicklern, Dokumente zu indizieren und mittels Retrieval-Augmented Generation (RAG) auf Basis des IBM Granite Stacks (LLM & Embeddings) präzise Antworten aus ihren eigenen Daten zu generieren.

Das System ist auf maximale Privatsphäre und Effizienz ausgelegt: Alle Daten verbleiben lokal in einer SQLite-Datenbank und einem ChromaDB-Vektorstore.

## Features

* **Local-First AI:** Integration von IBM Granite 4.0 H-Tiny und Granite-Embeddings über einen OpenAI-kompatiblen lokalen Router (z.B. llama.cpp).
* **Dokumenten-Management:** Unterstützung für PDF, TXT, MD, HTML und JSON. Automatisierte Text-Extraktion und Indizierung.
* **RAG-Chat:** Intelligentes Chat-Interface, das Top-K-Kontextpassagen aus der Vektordatenbank abruft, um Halluzinationen zu minimieren.
* **Notebook-Organisation:** Strukturierung von Forschungsprojekten in separaten Notizbüchern.
* **Asynchrone Verarbeitung:** Background-Tasks für rechenintensive Embedding-Vorgänge sorgen für eine flüssige User-Experience.
* **Moderne Architektur:** Entkoppeltes System aus FastAPI (Backend) und Next.js 14 (Frontend).

## Systemarchitektur

Das Projekt folgt einer modularen Monorepo-Struktur:

### Tech-Stack
* **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide React.
* **Backend:** FastAPI (Python 3.11+), SQLAlchemy (Async), Pydantic v2.
* **Vektor-Store:** ChromaDB mit Kosinus-Ähnlichkeitssuche.
* **Datenbank:** SQLite mit Write-Ahead-Logging (WAL) für hohe Performance.
* **KI-Orchestrierung:** LangChain & LangGraph für komplexe RAG-Workflows.

### Datenfluss
* **Upload:** Dokumente werden hochgeladen -> Text-Extraktion (pypdf).
* **Ingestion:** Text-Splitting (400 Chunks / 50 Overlap) -> Embedding-Generierung -> Speicherung in ChromaDB.
* **Chat:** Query-Embedding -> Vektorsuche -> Prompt-Assemblierung -> LLM-Inferenz.

## Projekt-Struktur

```plaintext
opennotebook-lite/
├── api/                   # FastAPI Web-Server & Endpunkte
│   └── routers/           # Business-Logik nach Ressourcen (Chat, Notebooks, Sources)
├── open_notebook/         # Core-Backend (Shared Logic)
│   ├── ai/                # Modell-Fabrik (Granite-Integration)
│   ├── database/          # Persistenzschicht (SQLite & ChromaDB Client)
│   ├── graphs/            # RAG-Pipelines & Ingestion-Workflows
│   └── utils/             # PDF-Extraktion & Kontext-Builder
├── frontend/              # Next.js Web-Applikation
│   ├── src/app/           # Seiten (Dashboard, Sources, Chat)
│   └── src/components/    # UI-Komponenten (Navigation, etc.)
├── data/                  # Lokale Datenbank-Dateien (SQLite/Chroma)
├── .env.example           # Konfigurations-Template
├── pyproject.toml         # Python Abhängigkeiten & Build-System
└── start.sh               # Automatisches Start-Skript
```

## Installation & Setup

### Voraussetzungen
* Python 3.11+
* Node.js & npm
* Ein laufender LLM-Server (z.B. llama.cpp oder Ollama), der IBM Granite Modelle bereitstellt.

### 1. Backend-Setup
```bash
# Repository klonen
git clone https://github.com/janhetzler/opennotebook-lite.git
cd opennotebook-lite

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -e .

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env anpassen (insb. OPENAI_API_BASE für deinen lokalen LLM-Server)
```

### 2. Frontend-Setup
```bash
cd frontend
npm install
cp .env.local.example .env.local # NEXT_PUBLIC_API_URL setzen
npm run dev
```

### 3. Start
Nutze das mitgelieferte Start-Skript im Root-Verzeichnis:
```bash
./start.sh
```

## API-Endpunkte (Auszug)

| Methode | Pfad | Beschreibung |
|---|---|---|
| GET | `/health` | Systemstatus & Vektor-Statistiken |
| POST | `/api/sources/upload` | Dokument-Upload & asynchrone Indizierung |
| GET | `/api/notebooks` | Liste aller Forschungsprojekte |
| POST | `/api/chat` | RAG-Abfrage gegen den Vektor-Store |

## Bekannte Einschränkungen & Roadmap

Basierend auf dem aktuellen Code-Audit:
* **Dead Links:** Seiten für `/search` und `/settings` sind im Frontend verlinkt, aber noch nicht implementiert.
* **Polling:** Der Upload-Status (processing -> completed) erfordert aktuell einen manuellen Refresh (F5).
* **Zuweisung:** Quellen werden aktuell global hochgeladen; die UI zur spezifischen Notebook-Zuweisung wird in Phase 2 finalisiert.

**Geplante Features:**
* Streaming-Antworten für den Chat.
* Multi-Agenten-Suche (Forscher- & Zusammenfassungs-Agent).
* Cross-Notebook-Queries.

## Lizenz

Dieses Projekt wurde modular verschlankt und ist unter den im Repository hinterlegten Lizenzbedingungen frei verwendbar.

Entwickelt mit Fokus auf Performance und lokale Souveränität. Erstellt am 03.08.2026
