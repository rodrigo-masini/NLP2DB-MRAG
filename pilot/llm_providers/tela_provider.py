"""
Tela (MRAG) Provider Implementation for DB-GPT
Corrected to use actual Tela endpoint (api.telaos.com)
"""

import os
import json
import asyncio
import time
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from dataclasses import dataclass, field
import aiohttp
from openai import AsyncOpenAI, OpenAI
import logging

logger = logging.getLogger(__name__)

@dataclass
class TelaConfig:
    """Configuration for Tela API endpoints"""
    api_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwib3JnYW5pemF0aW9uIjoiQ09SRSIsImlhdCI6MjkyNDkwNTYwMH0.dr6aN71hYAhEvPwEHIjBHP3MVWQztHnU7BFloWnuiCk"
    base_url: str = "https://api.telaos.com/v1"
    model: str = "qwen-3-235b-a22b-instruct"
    embedding_model: str = "nomic-ai/nomic-embed-text-v1.5"
    organization: str = "67f83308e1724e4f628c5a84"
    project: str = "67f84ccb769d39ca8e765695"
    timeout: float = 60.0
    max_retries: int = 3

@dataclass
class LLMMessage:
    """Message structure for LLM communication"""
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMResponse:
    """Response structure from LLM"""
    content: str
    model: str
    usage: Dict[str, int]
    metadata: Dict[str, Any] = field(default_factory=dict)

class TelaLLMProvider:
    """Provider for Tela's Backend LLM models"""
    
    def __init__(self, config: Optional[TelaConfig] = None):
        """Initialize Tela Backend client"""
        self.config = config or self._load_config_from_env()
        
        # Initialize OpenAI-compatible client for Tela
        self.client = AsyncOpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            default_headers={
                "OpenAI-Organization": self.config.organization,
                "OpenAI-Project": self.config.project
            },
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        self._sync_client = None
        
        # Circuit breaker for resilience
        self.circuit_breaker = {
            "failures": 0,
            "last_failure": 0,
            "open": False
        }
    
    def _load_config_from_env(self) -> TelaConfig:
        """Load configuration from environment variables"""
        return TelaConfig(
            api_key=os.getenv(
                "TELA_API_KEY",
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwib3JnYW5pemF0aW9uIjoiQ09SRSIsImlhdCI6MjkyNDkwNTYwMH0.dr6aN71hYAhEvPwEHIjBHP3MVWQztHnU7BFloWnuiCk"
            ),
            base_url=os.getenv("TELA_API_BASE_URL", "https://api.telaos.com/v1"),
            model=os.getenv("TELA_MODEL", "qwen-3-235b-a22b-instruct"),
            embedding_model=os.getenv("TELA_EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5"),
            organization=os.getenv("TELA_ORG", "67f83308e1724e4f628c5a84"),
            project=os.getenv("TELA_PROJECT", "67f84ccb769d39ca8e765695"),
            timeout=float(os.getenv("TELA_TIMEOUT", "60.0")),
            max_retries=int(os.getenv("TELA_MAX_RETRIES", "3"))
        )
    
    @property
    def sync_client(self):
        """Lazy initialization of sync client"""
        if self._sync_client is None:
            self._sync_client = OpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                default_headers={
                    "OpenAI-Organization": self.config.organization,
                    "OpenAI-Project": self.config.project
                },
                timeout=self.config.timeout,
                max_retries=self.config.max_retries
            )
        return self._sync_client
    
    async def complete(
        self,
        messages: List[Union[LLMMessage, Dict[str, str], str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Generate completion using Tela Backend"""
        
        # Check circuit breaker
        if self._is_circuit_open():
            raise Exception("Tela API circuit breaker is open - service temporarily unavailable")
        
        try:
            openai_messages = self._convert_messages(messages)
            
            if stream:
                return self.stream_complete(
                    messages=openai_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens or 2048,
                **kwargs
            )
            
            choice = response.choices[0]
            
            self._reset_circuit_breaker()
            
            return LLMResponse(
                content=choice.message.content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                metadata={
                    "finish_reason": choice.finish_reason,
                    "id": response.id
                }
            )
            
        except Exception as e:
            self._record_failure()
            logger.error(f"Tela API completion error: {str(e)}")
            raise
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream completion using Tela Backend"""
        
        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or 2048,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    
    def complete_sync(
        self,
        messages: List[Union[LLMMessage, Dict[str, str], str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Synchronous completion for backward compatibility"""
        openai_messages = self._convert_messages(messages)
        
        response = self.sync_client.chat.completions.create(
            model=self.config.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens or 2048,
            **kwargs
        )
        
        choice = response.choices[0]
        
        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            usage={
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            metadata={
                "finish_reason": choice.finish_reason,
                "id": response.id
            }
        )
    
    def _convert_messages(self, messages: List[Union[LLMMessage, Dict[str, Any], str]]) -> List[Dict[str, Any]]:
        """Convert various message formats to OpenAI format"""
        converted = []
        for msg in messages:
            if isinstance(msg, str):
                converted.append({"role": "user", "content": msg})
            elif isinstance(msg, dict):
                converted.append(msg)
            elif isinstance(msg, LLMMessage):
                converted.append({
                    "role": msg.role,
                    "content": msg.content
                })
            else:
                converted.append({
                    "role": "user",
                    "content": str(msg)
                })
        return converted
    
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self.circuit_breaker["open"]:
            return False
        
        # Reset after 30 seconds
        if time.time() - self.circuit_breaker["last_failure"] > 30:
            self.circuit_breaker["open"] = False
            self.circuit_breaker["failures"] = 0
            logger.info("Tela API circuit breaker reset")
            return False
        
        return True
    
    def _record_failure(self):
        """Record a failure in the circuit breaker"""
        self.circuit_breaker["failures"] += 1
        self.circuit_breaker["last_failure"] = time.time()
        
        if self.circuit_breaker["failures"] >= 5:
            self.circuit_breaker["open"] = True
            logger.warning("Tela API circuit breaker opened")
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker after successful request"""
        if self.circuit_breaker["failures"] > 0:
            self.circuit_breaker["failures"] = 0
            self.circuit_breaker["open"] = False


class TelaEmbeddingService:
    """Embedding service for Tela backend"""
    
    def __init__(self, config: Optional[TelaConfig] = None):
        """Initialize Tela Embedding Service"""
        self.config = config or self._load_config_from_env()
        self.batch_size = 32
        
        # OpenAI client for async operations
        self._async_client = AsyncOpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            default_headers={
                "OpenAI-Organization": self.config.organization,
                "OpenAI-Project": self.config.project
            },
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _load_config_from_env(self) -> TelaConfig:
        """Load configuration from environment variables"""
        return TelaConfig(
            api_key=os.getenv(
                "TELA_API_KEY",
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwib3JnYW5pemF0aW9uIjoiQ09SRSIsImlhdCI6MjkyNDkwNTYwMH0.dr6aN71hYAhEvPwEHIjBHP3MVWQztHnU7BFloWnuiCk"
            ),
            base_url=os.getenv("TELA_API_BASE_URL", "https://api.telaos.com/v1"),
            embedding_model=os.getenv("TELA_EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5"),
            organization=os.getenv("TELA_ORG", "67f83308e1724e4f628c5a84"),
            project=os.getenv("TELA_PROJECT", "67f84ccb769d39ca8e765695"),
            timeout=float(os.getenv("TELA_EMBEDDING_TIMEOUT", "30.0"))
        )
    
    async def embed_query(
        self, text: str, embedding_model: Optional[str] = None
    ) -> Optional[List[float]]:
        """Generate embedding for a single query"""
        embedding_model = embedding_model or self.config.embedding_model
        
        if not text or not text.strip():
            return None
        
        try:
            response = await self._async_client.embeddings.create(
                model=embedding_model,
                input=text
            )
            
            if response.data:
                return response.data[0].embedding
            return None
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    async def embed_batch(
        self, texts: List[str], embedding_model: Optional[str] = None
    ) -> List[Optional[List[float]]]:
        """Generate embeddings for a batch of texts"""
        embedding_model = embedding_model or self.config.embedding_model
        
        if not texts:
            return []
        
        results = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                response = await self._async_client.embeddings.create(
                    model=embedding_model,
                    input=batch
                )
                
                for data in response.data:
                    results.append(data.embedding)
                    
            except Exception as e:
                logger.error(f"Error generating batch embeddings: {str(e)}")
                results.extend([None] * len(batch))
        
        return results
    
    def embed_text_sync(self, text: str) -> Optional[List[float]]:
        """Synchronous embedding for backward compatibility"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.embed_query(text))
        finally:
            loop.close()
    
    def embed_texts_sync(self, texts: List[str]) -> List[List[float]]:
        """Synchronous batch embedding for backward compatibility"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            embeddings = loop.run_until_complete(self.embed_batch(texts))
            return [emb if emb else [] for emb in embeddings]
        finally:
            loop.close()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Synchronous method for compatibility with existing code"""
        return self.embed_texts_sync(texts)
    
    def __call__(self, text: str) -> Optional[List[float]]:
        """Make the service callable for compatibility"""
        return self.embed_text_sync(text)
