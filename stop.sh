#!/usr/bin/env bash
set -e

echo "=== Open Notebook Light v2.1.0-light wird gestoppt ==="

echo "[+] Beende FastAPI Backend..."
if pkill -f "uvicorn api.main:app"; then
    echo "    Backend erfolgreich beendet."
else
    echo "    Kein laufendes Backend gefunden."
fi

echo "[+] Beende Next.js Frontend..."
fuser -k 3000/tcp 2>/dev/null || true
pkill -f "next-server" || true
if pkill -f "next start"; then
    echo "    Frontend erfolgreich beendet."
else
    echo "    Kein laufendes Frontend gefunden (oder bereits beendet)."
fi

echo "=== Stopvorgang abgeschlossen ==="
