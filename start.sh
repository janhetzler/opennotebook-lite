#!/usr/bin/env bash
set -e

echo "=== Open Notebook Light v2.1.0-light wird gestartet ==="

# Wechsle ins Arbeitsverzeichnis des Skripts (idempotent)
cd "$(dirname "$0")"

# 1. Backend Umgebung prüfen
if [ ! -f .env ]; then
    echo "[!] Keine .env Datei gefunden. Erstelle .env aus .env.example..."
    cp .env.example .env
fi

export $(grep -v "^#" .env | xargs)
mkdir -p $(dirname "${SQLITE_DB_PATH:-/app/data/notebook.db}")
mkdir -p "${CHROMA_DB_PATH:-/app/data/chroma}"

# 2. Backend starten (im Hintergrund)
echo "[+] Starte FastAPI Backend..."
# Idempotenz: Sicherstellen, dass alte Instanzen beendet sind
pkill -f "uvicorn api.main:app" || true
sleep 1

if [ -f "venv/bin/uvicorn" ]; then
    nohup venv/bin/uvicorn api.main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}" --env-file .env --reload > backend.log 2>&1 &
    echo "    Backend gestartet (Log: backend.log)"
else
    echo "[!] Uvicorn in venv/bin/ nicht gefunden. Läuft die VM?"
    exit 1
fi

# 3. Frontend starten (im Hintergrund)
echo "[+] Starte Next.js Frontend..."
cd frontend
# Idempotenz: Sicherstellen, dass alte Instanzen beendet sind (Port 3000 freigeben)
fuser -k 3000/tcp 2>/dev/null || true
pkill -f "next-server" || true
pkill -f "next start" || true
sleep 1

if [ -d ".next" ]; then
    nohup npm run start > frontend.log 2>&1 &
    echo "    Frontend gestartet (Log: frontend/frontend.log)"
else
    echo "[!] Kein Production-Build gefunden (.next Verzeichnis fehlt). Bitte erst 'npm run build' ausführen."
    exit 1
fi

echo "=== Startvorgang abgeschlossen ==="
