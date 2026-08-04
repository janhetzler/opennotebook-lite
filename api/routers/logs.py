import os
import httpx
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from loguru import logger

router = APIRouter()

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/app/data/logs/open_notebook.log")

class LogsResponse(BaseModel):
    logs: str
    github_token_configured: bool

@router.get("", response_model=LogsResponse)
async def get_logs(lines: int = 1000):
    """Liest die letzten N Zeilen der Logdatei."""
    has_token = bool(os.getenv("GITHUB_TOKEN"))
    if not os.path.exists(LOG_FILE_PATH):
        return LogsResponse(logs="Bisher keine Logs vorhanden.", github_token_configured=has_token)
    
    try:
        # Lese die letzten N Zeilen (speicherfreundlich bei großen Dateien)
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            # Bei riesigen Dateien wäre ein seek von hinten effizienter, 
            # für <10MB reicht readlines().
            all_lines = f.readlines()
            tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            content = "".join(tail_lines)
            
        return LogsResponse(logs=content, github_token_configured=has_token)
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Logs: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Lesen der Logdatei.")

@router.get("/download")
async def download_logs():
    """Bietet die Logdatei als Download an."""
    if not os.path.exists(LOG_FILE_PATH):
        raise HTTPException(status_code=404, detail="Logdatei existiert noch nicht.")
    
    return FileResponse(
        path=LOG_FILE_PATH, 
        filename="open_notebook_backend.log",
        media_type="text/plain"
    )

@router.post("/github")
async def push_to_github():
    """Erstellt ein geheimes GitHub Gist mit dem aktuellen Log-Inhalt."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise HTTPException(status_code=400, detail="GITHUB_TOKEN ist nicht konfiguriert.")
    
    if not os.path.exists(LOG_FILE_PATH):
        raise HTTPException(status_code=404, detail="Keine Logdatei zum Exportieren vorhanden.")
        
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            
        payload = {
            "description": "Open Notebook Light - Backend Logs (Debug)",
            "public": False,
            "files": {
                "open_notebook_backend.log": {
                    "content": content
                }
            }
        }
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.github.com/gists", json=payload, headers=headers)
            
        if response.status_code == 201:
            gist_url = response.json().get("html_url")
            logger.info(f"Logs erfolgreich zu GitHub Gist exportiert: {gist_url}")
            return {"status": "success", "url": gist_url}
        else:
            logger.error(f"GitHub API Fehler: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="GitHub API Fehler beim Erstellen des Gists.")
            
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim GitHub-Export: {e}")
        raise HTTPException(status_code=500, detail=str(e))
