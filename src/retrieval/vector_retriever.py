# src/retrieval/vector_retriever.py
from typing import List, Dict, Any, Optional
from src.knowledge_base.vector_store import VectorStore
from src.ingestion.embedder import Embedder
from src.knowledge_base.cache import CacheStore
from loguru import logger
import hashlib


class VectorRetriever:
    """Vector similarity search retrieval"""

    def __init__(self):
        self.vector_store = VectorStore()
        self.embedder = Embedder()
        self.cache = CacheStore()

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""

        # Create cache key
        cache_key = self._create_cache_key(query, top_k, filters)

        # Check cache first
        if use_cache:
            cached_results = self.cache.get(cache_key)
            if cached_results:
                logger.info("Retrieved results from cache")
                return cached_results

        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_text(query)

            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding, n_results=top_k, where=filters
            )

            # Format results
            formatted_results = self._format_results(results)

            # Cache results for 1 hour
            if use_cache:
                self.cache.set(cache_key, formatted_results, expire=3600)

            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format ChromaDB results"""
        formatted = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        for i in range(len(documents)):
            formatted.append(
                {
                    "id": ids[i],
                    "content": documents[i],
                    "metadata": metadatas[i],
                    "similarity_score": 1
                    - distances[i],  # Convert distance to similarity
                    "retrieval_method": "vector_search",
                }
            )

        return formatted

    def _create_cache_key(
        self, query: str, top_k: int, filters: Optional[Dict[str, Any]]
    ) -> str:
        """Create cache key for query"""
        content = f"vector_search:{query}:{top_k}:{filters}"
        return f"search:{hashlib.md5(content.encode()).hexdigest()}"

    def search_by_document(
        self, doc_id: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search within a specific document"""
        filters = {"doc_id": doc_id}
        return self.search(query, top_k, filters)
