from typing import Optional, List
from pilot.configs.config import Config
from pilot.source_embedding.source_embedding import SourceEmbedding
from pilot.vector_store.connector import VectorStoreConnector

CFG = Config()

# Mapping file extensions to their respective loader classes
# This part is simplified as the loaders themselves are mostly compatible

class KnowledgeEmbedding:
    def __init__(self, file_path: Optional[str] = None, vector_store_config: Optional[dict] = None, **kwargs):
        self.file_path = file_path
        self.vector_store_config = vector_store_config
        self.embeddings = vector_store_config.get("embeddings") # Should be TelaEmbeddingService

    async def knowledge_embedding(self):
        # Logic to select the right document loader based on file_path extension
        # For simplicity, assuming a generic loader here.
        # In a full implementation, you'd import and use PDFEmbedding, CSVEmbedding etc.
        # from pilot.source_embedding.pdf_embedding import PDFEmbedding
        # loader = PDFEmbedding(self.file_path, self.vector_store_config)
        # await loader.source_embedding()
        pass # Placeholder for actual loading logic

    async def similar_search(self, text: str, topk: int) -> List:
        """Performs a similarity search in the vector store."""
        vector_client = VectorStoreConnector(CFG.VECTOR_STORE_TYPE, self.vector_store_config)
        return await vector_client.similar_search(text, topk)

    async def vector_exist(self) -> bool:
        """Checks if the vector store collection exists."""
        vector_client = VectorStoreConnector(CFG.VECTOR_STORE_TYPE, self.vector_store_config)
        return await vector_client.vector_name_exists()
