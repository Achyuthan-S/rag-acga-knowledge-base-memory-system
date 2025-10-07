#!/usr/bin/env python3
"""
Benchmark script for RAG Knowledge Base system
Tests performance across various operations and scenarios
"""

import time
import statistics
from typing import List, Dict, Any
from loguru import logger
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.processor import IngestionProcessor
from src.ingestion.embedder import Embedder
from src.retrieval.hybrid_retriever import HybridRetriever
from src.knowledge_base.vector_store import VectorStore
from src.knowledge_base.cache import CacheStore
from src.llm.client import LLMClient
from config.settings import get_settings


class BenchmarkRunner:
    def __init__(self):
        self.settings = get_settings()
        self.results = {}

    def time_operation(self, func, *args, runs=5, **kwargs):
        """Time an operation over multiple runs"""
        times = []
        for _ in range(runs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            times.append(end - start)

        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            "runs": runs,
        }

    def benchmark_embedding_generation(self):
        """Benchmark embedding generation speed"""
        logger.info("\n=== Benchmarking Embedding Generation ===")
        embedder = Embedder()

        test_texts = [
            "Short text",
            "Medium length text with more words to process and convert into embeddings",
            "Very long text " * 50,  # ~500 words
        ]

        results = {}
        for i, text in enumerate(test_texts):
            word_count = len(text.split())
            logger.info(f"Testing text with {word_count} words...")

            timing = self.time_operation(embedder.embed_text, text, runs=3)
            results[f"text_{word_count}_words"] = {
                "timing": timing,
                "chars": len(text),
                "words": word_count,
            }
            logger.info(
                f"  Mean: {timing['mean']:.3f}s, Median: {timing['median']:.3f}s"
            )

        self.results["embedding_generation"] = results
        return results

    def benchmark_batch_embedding(self):
        """Benchmark batch embedding performance"""
        logger.info("\n=== Benchmarking Batch Embedding ===")
        embedder = Embedder()

        batch_sizes = [1, 5, 10, 20, 50]
        test_text = "This is a test chunk for embedding generation. " * 20

        results = {}
        for batch_size in batch_sizes:
            texts = [f"{test_text} Chunk {i}" for i in range(batch_size)]
            logger.info(f"Testing batch size: {batch_size}...")

            timing = self.time_operation(embedder.embed_batch, texts, runs=3)
            results[f"batch_{batch_size}"] = {
                "timing": timing,
                "batch_size": batch_size,
                "per_item": timing["mean"] / batch_size,
            }
            logger.info(
                f"  Mean: {timing['mean']:.3f}s, Per item: {timing['mean'] / batch_size:.3f}s"
            )

        self.results["batch_embedding"] = results
        return results

    def benchmark_vector_search(self):
        """Benchmark vector search performance"""
        logger.info("\n=== Benchmarking Vector Search ===")

        vector_store = VectorStore()
        embedder = Embedder()

        # Get document count
        doc_count = vector_store.count()
        logger.info(f"Current vector store size: {doc_count} documents")

        if doc_count == 0:
            logger.warning("No documents in vector store. Skipping search benchmark.")
            return {}

        test_queries = [
            "What is machine learning?",
            "How do vector databases work?",
            "Explain retrieval augmented generation",
        ]

        results = {}
        for k in [1, 5, 10, 20]:
            logger.info(f"Testing top-{k} search...")
            times = []

            for query in test_queries:
                query_embedding = embedder.embed_text(query)
                start = time.time()
                vector_store.search(query_embedding, n_results=k)
                end = time.time()
                times.append(end - start)

            results[f"top_{k}"] = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "min": min(times),
                "max": max(times),
                "k_value": k,
            }
            logger.info(f"  Mean: {statistics.mean(times):.3f}s")

        self.results["vector_search"] = results
        return results

    def benchmark_hybrid_retrieval(self):
        """Benchmark hybrid retrieval strategies"""
        logger.info("\n=== Benchmarking Hybrid Retrieval ===")

        retriever = HybridRetriever()

        test_queries = [
            ("What is RAG?", "vector_only"),
            ("How are concepts related?", "graph_only"),
            ("Explain machine learning", "combined"),
            ("What is testing?", "auto"),
        ]

        results = {}
        for query, strategy in test_queries:
            logger.info(f"Testing {strategy} strategy...")

            timing = self.time_operation(
                retriever.search, query, strategy=strategy, top_k=5, runs=3
            )
            results[strategy] = {"timing": timing, "query": query}
            logger.info(f"  Mean: {timing['mean']:.3f}s")

        self.results["hybrid_retrieval"] = results
        return results

    def benchmark_cache_performance(self):
        """Benchmark cache hit/miss performance"""
        logger.info("\n=== Benchmarking Cache Performance ===")

        cache = CacheStore()
        test_key = "benchmark_test_key"
        test_value = {"result": "test data" * 100}

        # Cache write
        write_timing = self.time_operation(
            cache.set, test_key, test_value, expire=3600, runs=10
        )
        logger.info(f"Cache write - Mean: {write_timing['mean'] * 1000:.2f}ms")

        # Cache read (hit)
        read_timing = self.time_operation(cache.get, test_key, runs=10)
        logger.info(f"Cache read (hit) - Mean: {read_timing['mean'] * 1000:.2f}ms")

        # Cache read (miss)
        miss_timing = self.time_operation(cache.get, "nonexistent_key", runs=10)
        logger.info(f"Cache read (miss) - Mean: {miss_timing['mean'] * 1000:.2f}ms")

        # Cleanup
        cache.delete(test_key)

        self.results["cache_performance"] = {
            "write": write_timing,
            "read_hit": read_timing,
            "read_miss": miss_timing,
            "speedup": write_timing["mean"] / read_timing["mean"]
            if read_timing["mean"] > 0
            else 0,
        }

        return self.results["cache_performance"]

    def benchmark_ingestion_pipeline(self):
        """Benchmark full ingestion pipeline"""
        logger.info("\n=== Benchmarking Ingestion Pipeline ===")

        processor = IngestionProcessor()

        test_documents = [
            ("Short doc", "This is a short test document." * 5),
            ("Medium doc", "This is a medium length document. " * 50),
            ("Long doc", "This is a long document with lots of content. " * 200),
        ]

        results = {}
        for name, content in test_documents:
            word_count = len(content.split())
            logger.info(f"Testing {name} ({word_count} words)...")

            timing = self.time_operation(
                processor.process_text, content, metadata={"test": "benchmark"}, runs=2
            )

            results[name] = {
                "timing": timing,
                "words": word_count,
                "chars": len(content),
                "words_per_second": word_count / timing["mean"]
                if timing["mean"] > 0
                else 0,
            }
            logger.info(
                f"  Mean: {timing['mean']:.3f}s, {results[name]['words_per_second']:.0f} words/s"
            )

        self.results["ingestion_pipeline"] = results
        return results

    def benchmark_llm_operations(self):
        """Benchmark LLM operations"""
        logger.info("\n=== Benchmarking LLM Operations ===")

        client = LLMClient()

        # Embedding generation
        logger.info("Testing embedding generation...")
        embed_timing = self.time_operation(
            client.generate_embedding, "Test text for embedding", runs=3
        )
        logger.info(f"  Mean: {embed_timing['mean']:.3f}s")

        # Response generation
        logger.info("Testing response generation...")
        messages = [{"role": "user", "content": "Say hello in one word."}]
        response_timing = self.time_operation(
            client.generate_response, messages, runs=2
        )
        logger.info(f"  Mean: {response_timing['mean']:.3f}s")

        self.results["llm_operations"] = {
            "embedding": embed_timing,
            "response": response_timing,
        }

        return self.results["llm_operations"]

    def benchmark_end_to_end_query(self):
        """Benchmark complete end-to-end query flow"""
        logger.info("\n=== Benchmarking End-to-End Query ===")

        retriever = HybridRetriever()
        cache = CacheStore()

        test_query = "What is the meaning of life?"

        # Cold query (no cache)
        cache_key = f"query:{test_query}"
        cache.delete(cache_key)  # Ensure no cache

        logger.info("Testing cold query (no cache)...")
        cold_timing = self.time_operation(
            retriever.search, test_query, strategy="auto", top_k=5, runs=3
        )
        logger.info(f"  Mean: {cold_timing['mean']:.3f}s")

        # Warm query (with cache)
        logger.info("Testing warm query (with cache)...")
        # First query to populate cache
        retriever.search(test_query, strategy="auto", top_k=5)

        warm_timing = self.time_operation(
            retriever.search, test_query, strategy="auto", top_k=5, runs=5
        )
        logger.info(f"  Mean: {warm_timing['mean']:.3f}s")
        logger.info(f"  Speedup: {cold_timing['mean'] / warm_timing['mean']:.2f}x")

        self.results["end_to_end_query"] = {
            "cold": cold_timing,
            "warm": warm_timing,
            "speedup": cold_timing["mean"] / warm_timing["mean"]
            if warm_timing["mean"] > 0
            else 0,
        }

        return self.results["end_to_end_query"]

    def print_summary_report(self):
        """Print comprehensive summary report"""
        logger.info("\n" + "=" * 70)
        logger.info("BENCHMARK SUMMARY REPORT")
        logger.info("=" * 70)

        # Embedding Performance
        if "embedding_generation" in self.results:
            logger.info("\n📊 EMBEDDING GENERATION")
            for key, data in self.results["embedding_generation"].items():
                logger.info(
                    f"  {data['words']} words: {data['timing']['mean']:.3f}s ±{data['timing']['stdev']:.3f}s"
                )

        # Batch Embedding
        if "batch_embedding" in self.results:
            logger.info("\n📦 BATCH EMBEDDING")
            for key, data in self.results["batch_embedding"].items():
                logger.info(
                    f"  Batch {data['batch_size']}: {data['timing']['mean']:.3f}s ({data['per_item'] * 1000:.1f}ms/item)"
                )

        # Vector Search
        if "vector_search" in self.results:
            logger.info("\n🔍 VECTOR SEARCH")
            for key, data in self.results["vector_search"].items():
                logger.info(
                    f"  Top-{data['k_value']}: {data['mean']:.3f}s (range: {data['min']:.3f}s - {data['max']:.3f}s)"
                )

        # Hybrid Retrieval
        if "hybrid_retrieval" in self.results:
            logger.info("\n🔀 HYBRID RETRIEVAL")
            for strategy, data in self.results["hybrid_retrieval"].items():
                logger.info(
                    f"  {strategy}: {data['timing']['mean']:.3f}s ±{data['timing']['stdev']:.3f}s"
                )

        # Cache Performance
        if "cache_performance" in self.results:
            cache = self.results["cache_performance"]
            logger.info("\n⚡ CACHE PERFORMANCE")
            logger.info(f"  Write: {cache['write']['mean'] * 1000:.2f}ms")
            logger.info(f"  Read (hit): {cache['read_hit']['mean'] * 1000:.2f}ms")
            logger.info(f"  Read (miss): {cache['read_miss']['mean'] * 1000:.2f}ms")

        # Ingestion
        if "ingestion_pipeline" in self.results:
            logger.info("\n📥 INGESTION PIPELINE")
            for name, data in self.results["ingestion_pipeline"].items():
                logger.info(
                    f"  {name}: {data['timing']['mean']:.3f}s ({data['words_per_second']:.0f} words/s)"
                )

        # LLM Operations
        if "llm_operations" in self.results:
            llm = self.results["llm_operations"]
            logger.info("\n🤖 LLM OPERATIONS (Gemini)")
            logger.info(
                f"  Embedding: {llm['embedding']['mean']:.3f}s ±{llm['embedding']['stdev']:.3f}s"
            )
            logger.info(
                f"  Response: {llm['response']['mean']:.3f}s ±{llm['response']['stdev']:.3f}s"
            )

        # End-to-End
        if "end_to_end_query" in self.results:
            e2e = self.results["end_to_end_query"]
            logger.info("\n🎯 END-TO-END QUERY")
            logger.info(f"  Cold (no cache): {e2e['cold']['mean']:.3f}s")
            logger.info(f"  Warm (cached): {e2e['warm']['mean']:.3f}s")
            logger.info(f"  Cache speedup: {e2e['speedup']:.2f}x")

        logger.info("\n" + "=" * 70)
        logger.info(f"Provider: {self.settings.llm_provider.upper()}")
        logger.info(f"Model: {self.settings.llm_model}")
        logger.info(f"Embedding Model: {self.settings.embedding_model}")
        logger.info(f"Embedding Dimension: {self.settings.embedding_dimension}")
        logger.info("=" * 70 + "\n")


def main():
    """Run all benchmarks"""
    logger.info("Starting RAG Knowledge Base Benchmarks...")
    logger.info(f"Using {get_settings().llm_provider.upper()} provider\n")

    runner = BenchmarkRunner()

    try:
        # Run all benchmarks
        runner.benchmark_embedding_generation()
        runner.benchmark_batch_embedding()
        runner.benchmark_vector_search()
        runner.benchmark_cache_performance()
        runner.benchmark_hybrid_retrieval()
        runner.benchmark_ingestion_pipeline()
        runner.benchmark_llm_operations()
        runner.benchmark_end_to_end_query()

        # Print summary
        runner.print_summary_report()

        logger.info("✅ All benchmarks completed successfully!")

    except Exception as e:
        logger.error(f"❌ Benchmark failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
