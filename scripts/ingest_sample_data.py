# scripts/ingest_sample_data.py
#!/usr/bin/env python3
"""
Sample data ingestion script
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.processor import IngestionProcessor
from loguru import logger


def create_sample_documents():
    """Create sample documents for testing"""

    sample_docs = [
        {
            "filename": "intro_to_rag.txt",
            "content": """
            Retrieval-Augmented Generation (RAG) is a technique that enhances large language models
            by combining them with information retrieval systems. This approach allows the model to
            access external knowledge bases and provide more accurate, up-to-date responses.
            
            RAG systems typically consist of three main components:
            1. A vector database for storing document embeddings
            2. A retrieval mechanism to find relevant information
            3. A language model to generate responses based on retrieved context
            
            The benefits of RAG include improved accuracy, reduced hallucinations, and the ability
            to work with domain-specific knowledge without retraining the entire model.
            """,
            "metadata": {
                "source": "sample_intro_to_rag",
                "filename": "intro_to_rag.txt",
                "type": "text",
                "category": "education",
            },
        },
        {
            "filename": "vector_databases.txt",
            "content": """
            Vector databases are specialized database systems designed to store and query high-dimensional
            vectors efficiently. They are essential components of modern AI applications, particularly
            in semantic search and RAG systems.
            
            Popular vector databases include:
            - ChromaDB: An open-source embedding database
            - Pinecone: A managed vector database service
            - Weaviate: An open-source vector search engine
            - Qdrant: A vector similarity search engine
            
            These databases use algorithms like HNSW (Hierarchical Navigable Small World) and IVF
            (Inverted File Index) to perform fast approximate nearest neighbor searches.
            """,
            "metadata": {
                "source": "sample_vector_databases",
                "filename": "vector_databases.txt",
                "type": "text",
                "category": "technology",
            },
        },
        {
            "filename": "graph_databases.txt",
            "content": """
            Graph databases store data in nodes and relationships, making them ideal for representing
            connected information. Neo4j is one of the most popular graph databases, using the
            Cypher query language for data manipulation.
            
            Key concepts in graph databases:
            - Nodes: Represent entities (people, places, things)
            - Relationships: Connect nodes with typed connections
            - Properties: Key-value pairs attached to nodes and relationships
            - Labels: Group nodes into categories
            
            Graph databases excel at queries involving relationships and connections, such as
            finding paths between entities, recommendation systems, and social network analysis.
            """,
            "metadata": {
                "source": "sample_graph_databases",
                "filename": "graph_databases.txt",
                "type": "text",
                "category": "technology",
            },
        },
    ]

    return sample_docs


def main():
    """Main function to ingest sample data"""
    logger.info("Starting sample data ingestion...")

    try:
        # Initialize processor
        processor = IngestionProcessor()

        # Get sample documents
        sample_docs = create_sample_documents()

        # Process each document
        results = []
        for doc in sample_docs:
            logger.info(f"Processing: {doc['filename']}")

            result = processor.process_text(
                text=doc["content"], metadata=doc["metadata"]
            )

            results.append(result)

            if result.get("status") == "success":
                logger.info(
                    f"✅ Successfully processed {doc['filename']}: {result.get('chunks', 0)} chunks created"
                )
            else:
                logger.error(
                    f"❌ Failed to process {doc['filename']}: {result.get('error', 'Unknown error')}"
                )

        # Get final stats
        stats = processor.get_stats()

        logger.info(f"""
        
        📊 Ingestion Complete!
        =====================
        Total Documents: {stats["metadata_store"]["documents"]}
        Total Chunks: {stats["metadata_store"]["chunks"]}
        Vector Store Count: {stats["vector_store"]["count"]}
        
        """)

        return True

    except Exception as e:
        logger.error(f"Error during sample data ingestion: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
