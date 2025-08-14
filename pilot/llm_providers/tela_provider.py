"""TELA Backend Provider with Enhanced NLP to SQL Capabilities"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator

from openai import AsyncOpenAI
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine, text, exc

logger = logging.getLogger(__name__)

class SQLQuery(BaseModel):
    sql: str
    thoughts: str

class TelaLLMProvider:
    """Provider for TELA Large Language Models."""
    def __init__(self):
        self.api_key = os.getenv("TELA_API_KEY")
        self.base_url = os.getenv("TELA_API_BASE_URL", "https://api.telaos.com/v1")
        self.project = os.getenv("TELA_PROJECT")
        self.organization = os.getenv("TELA_ORG")
        self.model = os.getenv("TELA_MODEL", "qwen-3-235b-a22b-instruct")

        if not all([self.api_key, self.project, self.organization]):
            raise ValueError("TELA_API_KEY, TELA_PROJECT, and TELA_ORG must be set in .env")

        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers={
                "OpenAI-Organization": self.organization,
                "OpenAI-Project": self.project
            }
        )

    async def generate_stream(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the TELA API."""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"TELA API streaming error: {e}")
            yield f"Error: Could not get a streaming response. Details: {e}"

    async def generate(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
        """Generate a non-streaming response from the TELA API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"TELA API error: {e}")
            raise

class TelaEmbeddingService:
    """Provider for TELA Embedding Models."""
    def __init__(self):
        self.api_key = os.getenv("TELA_API_KEY")
        self.base_url = os.getenv("TELA_API_BASE_URL", "https://api.telaos.com/v1")
        self.project = os.getenv("TELA_PROJECT")
        self.organization = os.getenv("TELA_ORG")
        self.model = os.getenv("TELA_EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5")

        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers={
                "OpenAI-Organization": self.organization,
                "OpenAI-Project": self.project
            }
        )

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        if not texts: return []
        try:
            response = await self.client.embeddings.create(model=self.model, input=texts)
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"TELA embedding error: {e}")
            raise

    async def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return (await self.embed_documents([text]))[0]
