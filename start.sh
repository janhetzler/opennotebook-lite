#!/usr/bin/env bash
set -e
echo "=== Open Notebook Light v2.0.0-light wird gestartet ==="

if [ ! -f .env ]; then
    echo "[!] Keine .env Datei gefunden. Erstelle .env aus .env.example..."
    cp .env.example .env
fi

export $(grep -v "^#" .env | xargs)

mkdir -p $(dirname "${SQLITE_DB_PATH:-/app/data/notebook.db}")
mkdir -p "${CHROMA_DB_PATH:-/app/data/chroma}"

echo "[+] Starte Server auf ${API_HOST:-0.0.0.0}:${API_PORT:-8000}..."
exec uvicorn api.main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}" --reload
