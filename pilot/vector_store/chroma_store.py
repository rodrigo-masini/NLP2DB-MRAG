import os
import asyncio
from typing import List
from langchain.vectorstores import Chroma
from pilot.configs.model_config import KNOWLEDGE_UPLOAD_ROOT_PATH
from pilot.logs import logger
from pilot.vector_store.vector_store_base import VectorStoreBase

class ChromaStore(VectorStoreBase):
    """Chroma vector store."""

    def __init__(self, ctx: {}) -> None:
        self.ctx = ctx
        self.embedding_service = ctx["embeddings"]
        self.persist_dir = os.path.join(
            KNOWLEDGE_UPLOAD_ROOT_PATH, ctx["vector_store_name"] + ".vectordb"
        )
        # ChromaDB client is synchronous, we wrap its calls in async executors
        self.vector_store_client = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self # Langchain expects an object with embed_documents/embed_query
        )

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return await self.embedding_service.embed_documents(texts)

    async def embed_query(self, text: str) -> List[float]:
        return await self.embedding_service.embed_query(text)

    async def similar_search(self, text, topk) -> List:
        logger.info("ChromaStore similar search")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self.vector_store_client.similarity_search, text, topk
        )

    async def vector_name_exists(self) -> bool:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: os.path.exists(self.persist_dir) and len(os.listdir(self.persist_dir)) > 0
        )

    async def load_document(self, documents):
        logger.info("ChromaStore load document")
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, self.vector_store_client.add_texts, texts, metadatas
        )
        await loop.run_in_executor(None, self.vector_store_client.persist)
