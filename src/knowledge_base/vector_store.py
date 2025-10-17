# src/knowledge_base/vector_store.py
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from loguru import logger
from config.settings import get_settings


class VectorStore:
    def __init__(self):
        self.settings = get_settings()
        self.client = chromadb.PersistentClient(
            path=self.settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base", metadata={"hnsw:space": "cosine"}
        )
        logger.info("Vector store initialized")

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ):
        """Add documents to vector store"""
        try:
            self.collection.add(
                documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Search vector store"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise

    def delete_collection(self):
        """Delete collection"""
        self.client.delete_collection("knowledge_base")
        logger.info("Collection deleted")

    def count(self) -> int:
        """Get count of documents in vector store"""
        return self.collection.count()

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return {"count": self.collection.count(), "name": self.collection.name}
