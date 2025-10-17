# src/retrieval/hybrid_retriever.py
from typing import List, Dict, Any
from src.retrieval.vector_retriever import VectorRetriever
from src.retrieval.graph_retriever import GraphRetriever
from loguru import logger
import re


class HybridRetriever:
    """Hybrid retrieval combining vector and graph search"""

    def __init__(self):
        self.vector_retriever = VectorRetriever()
        self.graph_retriever = GraphRetriever()

    def search(
        self,
        query: str,
        strategy: str = "auto",
        top_k: int = 10,
        vector_weight: float = 0.7,
        graph_weight: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search with multiple strategies

        Strategies:
        - auto: Automatically determine best approach
        - vector_only: Vector search only
        - graph_only: Graph search only
        - combined: Combine both methods
        """

        if strategy == "auto":
            strategy = self._determine_strategy(query)

        logger.info(f"Using strategy: {strategy} for query: {query[:50]}...")

        if strategy == "vector_only":
            return self.vector_retriever.search(query, top_k)

        elif strategy == "graph_only":
            return self._graph_search_for_query(query, top_k)

        elif strategy == "combined":
            return self._combined_search(query, top_k, vector_weight, graph_weight)

        else:
            # Default to vector search
            return self.vector_retriever.search(query, top_k)

    def _determine_strategy(self, query: str) -> str:
        """Automatically determine best search strategy"""

        # Relationship keywords indicate graph search
        relationship_keywords = [
            "related to",
            "connected to",
            "relationship",
            "links",
            "network",
            "associated with",
            "connected",
            "relationship between",
            "how are",
            "connection",
            "link",
            "ties",
            "related",
            "associate",
        ]

        # Entity keywords
        entity_keywords = [
            "who is",
            "what is",
            "person",
            "organization",
            "company",
            "people",
            "entities",
            "actors",
        ]

        query_lower = query.lower()

        # Check for relationship queries
        if any(keyword in query_lower for keyword in relationship_keywords):
            return "graph_only"

        # Check for entity queries that might benefit from graph
        if any(keyword in query_lower for keyword in entity_keywords):
            return "combined"

        # Check for specific entity names (capitalized words)
        if re.search(r"\b[A-Z][a-z]+\b.*\b[A-Z][a-z]+\b", query):
            return "combined"

        # Default to vector search for semantic queries
        return "vector_only"

    def _graph_search_for_query(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform graph search based on query"""

        # Extract potential entity names (simple approach)
        entities = self._extract_entities_from_query(query)

        results = []

        for entity in entities:
            # Get related entities
            related = self.graph_retriever.find_related_entities(
                entity, max_depth=2, limit=top_k // len(entities) if entities else top_k
            )
            results.extend(related)

        # If no entities found, try property search
        if not results:
            results = self.graph_retriever.search_by_properties(limit=top_k)

        return results[:top_k]

    def _combined_search(
        self, query: str, top_k: int, vector_weight: float, graph_weight: float
    ) -> List[Dict[str, Any]]:
        """Combine vector and graph search results"""

        # Get results from both methods
        vector_results = self.vector_retriever.search(query, top_k)
        graph_results = self._graph_search_for_query(query, top_k)

        # Combine and score results
        combined_results = []

        # Add vector results with weighted scores
        for result in vector_results:
            result["combined_score"] = result.get("similarity_score", 0) * vector_weight
            result["search_methods"] = ["vector"]
            combined_results.append(result)

        # Add graph results with weighted scores
        for result in graph_results:
            # Create a similarity score based on graph distance
            distance = result.get("distance", 1)
            graph_score = 1.0 / distance if distance > 0 else 1.0

            result["combined_score"] = graph_score * graph_weight
            result["search_methods"] = ["graph"]
            combined_results.append(result)

        # Sort by combined score and remove duplicates
        combined_results.sort(key=lambda x: x.get("combined_score", 0), reverse=True)

        # Remove duplicates based on content similarity
        unique_results = self._deduplicate_results(combined_results)

        return unique_results[:top_k]

    def _extract_entities_from_query(self, query: str) -> List[str]:
        """Extract potential entity names from query"""

        # Simple entity extraction - look for capitalized words
        words = query.split()
        entities = []

        for word in words:
            # Remove punctuation
            clean_word = re.sub(r"[^\w]", "", word)

            # Check if it's a proper noun (capitalized)
            if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                entities.append(clean_word)

        return entities

    def _deduplicate_results(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""

        unique_results = []
        seen_content = set()

        for result in results:
            content = result.get("content", "")

            # Create a simple hash for duplicate detection
            content_hash = hash(content[:100]) if content else hash(str(result))

            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)

        return unique_results

    def search_with_context(
        self, query: str, context_entities: List[str] = None, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search with additional context entities"""

        if not context_entities:
            return self.search(query, top_k=top_k)

        # Expand search with context entities
        expanded_results = []

        # Regular search
        base_results = self.search(query, top_k=top_k // 2)
        expanded_results.extend(base_results)

        # Context-based graph search
        for entity in context_entities:
            related = self.graph_retriever.find_related_entities(
                entity, max_depth=1, limit=2
            )
            expanded_results.extend(related)

        # Deduplicate and sort
        unique_results = self._deduplicate_results(expanded_results)

        return unique_results[:top_k]
