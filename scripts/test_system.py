#!/usr/bin/env python3
# scripts/test_system.py
"""
System test script to verify all components are working
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
import time


def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing imports...")

    try:
        from config.settings import get_settings
        from src.ingestion.loader import DocumentLoader
        from src.ingestion.chunker import DocumentChunker
        from src.ingestion.embedder import Embedder
        from src.ingestion.processor import IngestionProcessor
        from src.knowledge_base.vector_store import VectorStore
        from src.knowledge_base.graph_store import GraphStore
        from src.knowledge_base.metadata_store import MetadataStore
        from src.knowledge_base.cache import CacheStore
        from src.memory.working_memory import WorkingMemory
        from src.memory.session_memory import SessionMemory
        from src.retrieval.vector_retriever import VectorRetriever
        from src.retrieval.graph_retriever import GraphRetriever
        from src.retrieval.hybrid_retriever import HybridRetriever
        from src.llm.client import LLMClient

        logger.info("✅ All imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        return False


def test_databases():
    """Test database connections"""
    logger.info("Testing database connections...")

    results = {}

    # Test Vector Store
    try:
        from src.knowledge_base.vector_store import VectorStore

        vs = VectorStore()
        count = vs.count()
        logger.info(f"✅ Vector Store: {count} documents")
        results["vector_store"] = True
    except Exception as e:
        logger.error(f"❌ Vector Store failed: {e}")
        results["vector_store"] = False

    # Test Graph Store
    try:
        from src.knowledge_base.graph_store import GraphStore

        gs = GraphStore()
        stats = gs.get_graph_stats()
        logger.info(
            f"✅ Graph Store: {stats['nodes']} nodes, {stats['relationships']} relationships"
        )
        gs.close()
        results["graph_store"] = True
    except Exception as e:
        logger.error(f"❌ Graph Store failed: {e}")
        results["graph_store"] = False

    # Test Metadata Store
    try:
        from src.knowledge_base.metadata_store import MetadataStore

        ms = MetadataStore()
        stats = ms.get_stats()
        logger.info(
            f"✅ Metadata Store: {stats['documents']} documents, {stats['chunks']} chunks"
        )
        ms.close()
        results["metadata_store"] = True
    except Exception as e:
        logger.error(f"❌ Metadata Store failed: {e}")
        results["metadata_store"] = False

    # Test Cache
    try:
        from src.knowledge_base.cache import CacheStore

        cache = CacheStore()
        if cache.ping():
            logger.info("✅ Cache Store: Connected")
            results["cache"] = True
        else:
            logger.error("❌ Cache Store: Not responding")
            results["cache"] = False
    except Exception as e:
        logger.error(f"❌ Cache Store failed: {e}")
        results["cache"] = False

    return all(results.values())


def test_ingestion():
    """Test document ingestion"""
    logger.info("Testing ingestion pipeline...")

    try:
        from src.ingestion.processor import IngestionProcessor

        processor = IngestionProcessor()

        # Test with sample text
        test_text = """
        This is a test document for the RAG Knowledge Base system.
        It contains information about testing and verification.
        The system should chunk this text and create embeddings.
        """

        result = processor.process_text(
            text=test_text,
            metadata={
                "source": "test_system_py",
                "type": "test",
                "category": "system_test",
            },
        )

        if result.get("status") == "success":
            logger.info(
                f"✅ Ingestion successful: {result.get('chunks', 0)} chunks created"
            )
            return True
        else:
            logger.error(f"❌ Ingestion failed: {result.get('error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Ingestion test failed: {e}")
        return False


def test_retrieval():
    """Test retrieval system"""
    logger.info("Testing retrieval system...")

    try:
        from src.retrieval.hybrid_retriever import HybridRetriever

        retriever = HybridRetriever()

        # Test query
        results = retriever.search(query="What is testing?", strategy="auto", top_k=5)

        logger.info(f"✅ Retrieval successful: {len(results)} results found")

        if results:
            logger.info(
                f"Top result score: {results[0].get('combined_score', results[0].get('similarity_score', 'N/A'))}"
            )

        return True

    except Exception as e:
        logger.error(f"❌ Retrieval test failed: {e}")
        return False


def test_memory():
    """Test memory system"""
    logger.info("Testing memory system...")

    try:
        from src.memory.session_memory import SessionMemory

        session = SessionMemory("test_session")

        # Add test interaction
        session.add_interaction(
            user_message="Test question",
            assistant_response="Test answer",
            metadata={"test": True},
        )

        # Retrieve history
        history = session.get_conversation_history()

        if history:
            logger.info(f"✅ Memory system working: {len(history)} interactions")
            return True
        else:
            logger.error("❌ Memory system failed: No history returned")
            return False

    except Exception as e:
        logger.error(f"❌ Memory test failed: {e}")
        return False


def test_llm_client():
    """Test LLM client (requires API key)"""
    logger.info("Testing LLM client...")

    try:
        from src.llm.client import LLMClient
        from config.settings import get_settings

        settings = get_settings()

        if not settings.openai_api_key or settings.openai_api_key == "":
            logger.warning("⚠️  OpenAI API key not set - skipping LLM test")
            return None

        client = LLMClient()

        # Test embedding
        embedding = client.generate_embedding("test text")

        if embedding and len(embedding) > 0:
            logger.info(
                f"✅ LLM Client working: Generated embedding of size {len(embedding)}"
            )
            return True
        else:
            logger.error("❌ LLM Client failed: No embedding generated")
            return False

    except Exception as e:
        logger.error(f"❌ LLM Client test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("RAG Knowledge Base - System Test")
    logger.info("=" * 60)

    tests = {
        "Imports": test_imports,
        "Databases": test_databases,
        "Ingestion": test_ingestion,
        "Retrieval": test_retrieval,
        "Memory": test_memory,
        "LLM Client": test_llm_client,
    }

    results = {}

    for test_name, test_func in tests.items():
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results[test_name] = result
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else ("⚠️  SKIP" if result is None else "❌ FAIL")
        logger.info(f"{test_name}: {status}")

    # Calculate pass rate (excluding skipped tests)
    completed_tests = [r for r in results.values() if r is not None]
    if completed_tests:
        pass_rate = sum(completed_tests) / len(completed_tests) * 100
        logger.info(
            f"\nPass Rate: {pass_rate:.1f}% ({sum(completed_tests)}/{len(completed_tests)} tests)"
        )

    logger.info("=" * 60)

    # Return success if all non-skipped tests passed
    return all(r for r in results.values() if r is not None)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
