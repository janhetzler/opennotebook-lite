"""
Open Notebook Light - In-Memory Digital PDF Reader
Modul: open_notebook/utils/pdf_extractor.py
Zweck: Liest digitale Text-PDFs direkt im Arbeitsspeicher via pypdf.
Version: 2.0.0-light
"""
__version__ = "2.0.0-light"

import io
from pypdf import PdfReader
from loguru import logger

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        extracted_pages = []

        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                extracted_pages.append(text)

        full_text = "\n\n".join(extracted_pages).strip()
        logger.debug(f"PDF-Extraktion erfolgreich: {len(full_text)} Zeichen aus {len(reader.pages)} Seiten.")
        return full_text
    except Exception as e:
        logger.error(f"Fehler bei der In-Memory PDF-Extraktion: {str(e)}")
        raise ValueError("Beschädigte oder ungültige PDF-Datei.") from e
