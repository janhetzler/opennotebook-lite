#!/usr/bin/env bash
set -e
echo "=== Open Notebook Light v2.0.0-light wird gestoppt ==="
PID=$(pgrep -f "uvicorn api.main:app" || true)
if [ -z "$PID" ]; then
    echo "[i] Kein laufender Open Notebook Light Server gefunden."
else
    echo "[+] Beende Uvicorn Prozess (PID: $PID)..."
    kill -15 $PID
    sleep 2
    echo "[+] Server erfolgreich gestoppt."
fi
