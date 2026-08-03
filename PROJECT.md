# Open Notebook Light Setup & Integration
Absoluter Speicherort: E:\open-computer\open-notebook-light\PROJECT.md

Dieses Projekt stellt eine schlanke, performante KI-Research-Engine mit einem lokal eingebetteten Persistenz-Setup auf der Debian-VM (Gast) bereit. Das System nutzt SQLite, ChromaDB und bindet sich an den Modell-Router auf dem Windows-Host an.

## System-Informationen
- **Gast-Betriebssystem:** Debian 13.5 (x86_64) (laufend in QEMU-WHPX)
- **Laufzeitumgebung:** Python 3.13 Virtualenv (`/app/open-notebook-light/venv`)
- **Web-Framework:** FastAPI (Port 8000 in der VM)
- **Modell-Backend:** `llama-server.exe` im Router-Modus (Host, Port 8080)
  - Endpoint: `http://10.0.2.2:8080/v1`
  - Chat-Modell: `granite-4.0-h-tiny-UD-Q4_K_XL.gguf`
  - Embedding-Modell: `granite-embedding-107m-multilingual-Q8_0.gguf`
- **Persistenz:**
  - SQLite (WAL-Modus aktiv, `/app/data/notebook.db`)
  - ChromaDB (PersistentClient, `/app/data/chroma`)

---

## Audit-Log
- [2026-08-03] **Erfolgreiche End-to-End-Integration:** Standalone-RAG-Abfragetest (`test_db.py`) durchgeführt. Ingestion-Fluss erfolgreich validiert:
  * Hochgeladene Chunks werden über den Windows-Host embeddet.
  * SQLite speichert relationale Metadaten im Status `completed`.
  * ChromaDB liefert bei Kosinus-Ähnlichkeitssuche das korrekte Ergebnis (Distanz `0.3170` bei Anfrage nach "lokale Vektorspeicher").
- [2026-08-03] **Umgebungskonfiguration korrigiert:** BOM (Byte Order Mark) aus `.env` entfernt und `load_dotenv()` in `api/main.py` und `test_db.py` integriert, da Uvicorn-Prozesse und Standalone-Skripte die Umgebungsvariablen sonst nicht zuverlässig geladen haben.
- [2026-08-03] **Verzeichnisstruktur & Pip Setup:** Repository in `/app/open-notebook-light` entpackt. Python3-dev-Pakete in der VM installiert, um C++ Compilation von `chroma-hnswlib` zu ermöglichen. `python-multipart` installiert (FastAPI Upload Dependency). SQLite-Datenbankpfad von Verzeichnis zu Datei korrigiert.
- [2026-08-02] **Vektor-Datenbank-Wrapper implementiert:** `open_notebook/database/vector_store.py` erstellt, um die fehlende ChromaDB-Kollektionsanbindung zu implementieren (idempotente IDs, Queries, Delete).

---

---

## Analyse der Arbeitsumgebung (Erstellte & Angepasste Dateien)

In den bisherigen Schritten wurden folgende Dateien und Verzeichnisse neu angelegt oder angepasst, um das System funktionsfähig zu machen:

### 1. `E:\open-computer\open-notebook-light\open_notebook\database\vector_store.py` (NEU)
* **Zweck:** Schließt die Lücke im Greenfield-Setup. Implementiert den kompletten ChromaDB PersistentClient-Wrapper (`add_chunks`, `search` und `delete_source_chunks`). Sorgt für die Vektorisierung und Indexierung der digitalisierten Textchunks mittels Kosinus-Metrik und speichert diese persistent unter `/app/data/chroma`.

### 2. `E:\open-computer\open-notebook-light\.env` (NEU)
* **Zweck:** Konfiguriert die Systemparameter für den Server. Setzt den standardmäßigen OpenAI-Modellpfad für Completions und Embeddings auf die Windows-Host-Schnittstelle (`10.0.2.2:8080/v1`) und spezifiziert die Pfade der SQLite-Datenbank und der Chroma-DB für die VM. (BOM wurde im Nachhinein entfernt).

### 3. `E:\open-computer\open-notebook-light\api\main.py` (MODIFIZIERT)
* **Zweck:** Ergänzt um den Import und Aufruf von `load_dotenv()`. Dadurch wird sichergestellt, dass beim Starten des Uvicorn-Webservers die in der `.env` definierten Umgebungsvariablen geladen sind und das System nicht fälschlicherweise auf die Standard-Ollama-IP `localhost:11434` zurückfällt.

### 4. `E:\open-computer\open-notebook-light\pyproject.toml` (MODIFIZIERT)
* **Zweck:** 
  - Die Python-Version-Prüfung wurde auf `<3.14,>=3.11` erweitert, da der VM-Gast mit Python 3.13 arbeitet.
  - Das Paket-Setup wurde um die Deklaration `[tool.setuptools] packages = ["open_notebook", "api"]` ergänzt, da die `setuptools` sonst aufgrund des Flat-Layouts (Multi-Package) den Build mit einem Fehler abgebrochen haben.
  - Die Versionsnummer wurde PEP440-konform auf `2.0.0.post1` geändert.

### 5. `E:\turboquant\models.ini` & `run_server_granite_router.ps1` (NEU auf Windows-Host)
* **Zweck:** 
  - `models.ini`: Deklariert die beiden IBM-Granite-Modelle für Completions und Embeddings für den `llama-server`.
  - `run_server_granite_router.ps1`: Startet den `llama-server.exe` im **Router-Modus** auf Port `8080`. Ohne Angabe eines `--model`-Flags lädt dieser Router eingehende Requests (Chat/Embeddings) dynamisch in den VRAM und verarbeitet sie parallel.

### 6. `E:\open-computer\open-notebook-light\test_db.py` (NEU)
* **Zweck:** Standalone-RAG-Testskript. Führt nach dem Laden der `.env` eine Test-Abfrage in ChromaDB und SQLite aus.

### 7. `E:\open-computer\open-notebook-light\test_chat.py` (NEU)
* **Zweck:** Multi-Turn-Chat-Testskript. Simuliert ein Zwei-Wege-Gespräch, um die Persistenz der Chat-Historie in der SQLite-Tabelle via LangGraph-Checkpointing (`AsyncSqliteSaver`) zu prüfen.

---

## Bekannte Fehler & Blocker (Frontend & API-Status)

### 🐛 Bug: Unerwarteter Parameter `repeat_penalty` in `ChatOpenAI`
Beim Ausführen des Multi-Turn-Chat-Tests (`test_chat.py`) bricht der Aufruf des Chat-Modells mit folgendem Fehler ab:
```
TypeError: AsyncCompletions.create() got an unexpected keyword argument 'repeat_penalty'. Did you mean 'presence_penalty'?
```
*Ursachenanalyse:* Das LangChain-OpenAI-Modul übersetzt das `repeat_penalty` Argument direkt in die API-Anfrage. Die offizielle OpenAI-API unterstützt dies jedoch nicht. Das Argument muss in `open_notebook/ai/models.py` gelöscht werden.

### ℹ️ Befund: Next.js-Frontend mit Mock-Daten
Die Analyse der Next.js-Dateien im Verzeichnis `frontend/src/app` ergab folgende Erklärung für das Verhalten der Oberfläche:
* **Chat-Antworten (`chat/page.tsx`):** Der RAG-Chat führt keine API-Anfragen an das FastAPI-Backend aus. In der Komponente ist ein `setTimeout`-Mock implementiert (Zeile 30–39), der nach einer Sekunde eine fest vordefinierte Antwort (`"[IBM Granite RAG Antwort]: ..."`) ausgibt.
* **Navigation/Settings:** Die Buttons (wie "Neues Notizbuch") besitzen keine Funktionalität oder Pfad-Routen-Anbindungen. Es handelt sich um ein statisches Design-Gerüst (Mockup).
* **Upload (`sources/page.tsx`):** Das Dokumenten-Upload-Formular ist voll funktionsfähig und sendet Anfragen direkt an das Backend (`${apiUrl}/api/sources/upload`). Die Ingestion in SQLite und ChromaDB wird dabei korrekt angestoßen.
* **Backend-Connect & CORS:** Das Backend ist auf Port `8000` via `allow_origins=["*"]` vollständig für das Next.js-Frontend (Port `3000`) erreichbar. Der Health-Check der Homepage funktioniert.

---

## Wichtige Pfade & URLs
- **Projekt-Pfad (Windows):** `E:\open-computer\open-notebook-light\`
- **Projekt-Pfad (VM):** `/app/open-notebook-light/`
- **Umgebungs-Konfiguration:** `/app/open-notebook-light/.env`
- **Vektor-Store-Klasse:** `/app/open-notebook-light/open_notebook/database/vector_store.py`
- **Interaktive Swagger-UI (VM):** `http://localhost:8000/docs`
- **Modell-Router (Host):** `http://10.0.2.2:8080/v1`
- **SQLite-Datenbank:** `/app/data/notebook.db`
- **ChromaDB-Verzeichnis:** `/app/data/chroma/`
- **RAG-Testskript (VM):** `/tmp/test_db.py`
- **Chat-Testskript (VM):** `/tmp/test_chat.py`

