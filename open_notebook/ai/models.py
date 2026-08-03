"""
Open Notebook Light - Lokale Modell-Fabrik (Gefixt)
Modul: open_notebook/ai/models.py
Zweck: Bereitstellung zentraler LangChain Chat- und Embedding-Clients.
Version: 2.0.1-light
"""

__version__ = "2.0.1-light"

import os
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from loguru import logger

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "granite-local-bypass")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "granite-4.0-h-tiny-UD-Q4_K_XL.gguf")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "granite-embedding-107m-multilingual-Q8_0.gguf")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.10"))
LLM_REQUEST_TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "120.0"))


class GraniteModelFactory:
    """Zentralisierte Fabrik für Chat- und Embedding-Modelle des IBM Granite Stacks."""

    @staticmethod
    def get_chat_model(temperature: Optional[float] = None) -> ChatOpenAI:
        temp = temperature if temperature is not None else LLM_TEMPERATURE
        logger.debug(f"Initialisiere ChatOpenAI -> Base: {OPENAI_API_BASE}, Model: {LLM_MODEL_NAME}")
        return ChatOpenAI(
            openai_api_base=OPENAI_API_BASE,
            openai_api_key=OPENAI_API_KEY,
            model_name=LLM_MODEL_NAME,
            temperature=temp,
            timeout=LLM_REQUEST_TIMEOUT,
            max_retries=2,
        )

    @staticmethod
    def get_embedding_model() -> OpenAIEmbeddings:
        logger.debug(f"Initialisiere OpenAIEmbeddings -> Base: {OPENAI_API_BASE}, Model: {EMBEDDING_MODEL_NAME}")
        return OpenAIEmbeddings(
            openai_api_base=OPENAI_API_BASE,
            openai_api_key=OPENAI_API_KEY,
            model=EMBEDDING_MODEL_NAME,
            check_embedding_ctx_length=False,
        )


async def get_default_chat_model(temperature: Optional[float] = None) -> ChatOpenAI:
    return GraniteModelFactory.get_chat_model(temperature=temperature)


async def get_default_embedding_model() -> OpenAIEmbeddings:
    return GraniteModelFactory.get_embedding_model()
