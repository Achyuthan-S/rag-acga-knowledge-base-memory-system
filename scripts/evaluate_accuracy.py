#!/usr/bin/env python3
"""
Simple accuracy measurement for RAG system
Requires: Ground truth test dataset
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.client import LLMClient


# Ground truth test dataset
# TODO: Replace with real test data
TEST_QUESTIONS = [
    {
        "question": "What is RAG?",
        "expected_keywords": ["retrieval", "augmented", "generation", "documents"],
        "relevant_doc_ids": ["intro_to_rag"],  # Based on ingested sample data
    },
    {
        "question": "What are vector databases?",
        "expected_keywords": ["vector", "embedding", "similarity", "search"],
        "relevant_doc_ids": ["vector_databases"],
    },
    {
        "question": "Explain graph databases",
        "expected_keywords": ["graph", "nodes", "relationships", "neo4j"],
        "relevant_doc_ids": ["graph_databases"],
    },
]


def calculate_precision_at_k(
    retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int = 5
) -> float:
    """Calculate Precision@K"""
    top_k = retrieved_doc_ids[:k]
    relevant_retrieved = len([doc for doc in top_k if doc in relevant_doc_ids])
    return relevant_retrieved / k if k > 0 else 0.0


def calculate_recall_at_k(
    retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int = 5
) -> float:
    """Calculate Recall@K"""
    if not relevant_doc_ids:
        return 0.0
    top_k = retrieved_doc_ids[:k]
    relevant_retrieved = len([doc for doc in top_k if doc in relevant_doc_ids])
    return relevant_retrieved / len(relevant_doc_ids)


def calculate_mrr(retrieved_doc_ids: List[str], relevant_doc_ids: List[str]) -> float:
    """Calculate Mean Reciprocal Rank"""
    for rank, doc_id in enumerate(retrieved_doc_ids, 1):
        if doc_id in relevant_doc_ids:
            return 1.0 / rank
    return 0.0


def evaluate_retrieval_accuracy():
    """Evaluate retrieval accuracy on test set"""
    logger.info("\n" + "=" * 70)
    logger.info("RAG SYSTEM ACCURACY EVALUATION")
    logger.info("=" * 70)

    retriever = HybridRetriever()

    all_precision = []
    all_recall = []
    all_mrr = []
    all_similarity_scores = []

    strategies = ["vector_only", "combined", "auto"]

    for strategy in strategies:
        logger.info(f"\n📊 Testing strategy: {strategy}")
        logger.info("-" * 70)

        strategy_precision = []
        strategy_recall = []
        strategy_mrr = []
        strategy_similarity = []

        for test_case in TEST_QUESTIONS:
            question = test_case["question"]
            relevant_doc_ids = test_case["relevant_doc_ids"]

            logger.info(f"\nQuestion: {question}")
            logger.info(f"Expected relevant docs: {relevant_doc_ids}")

            # Retrieve
            results = retriever.search(question, strategy=strategy, top_k=5)

            # Extract document IDs (simplified - depends on your metadata structure)
            retrieved_ids = []
            similarity_scores = []

            for result in results:
                # Try to extract doc ID from metadata
                metadata = result.get("metadata", {})
                doc_id = metadata.get("doc_id", metadata.get("source", "unknown"))

                # Simplify doc_id (remove file extensions, paths)
                if isinstance(doc_id, str):
                    doc_id = doc_id.split("/")[-1].split(".")[0]

                retrieved_ids.append(doc_id)

                # Get similarity score
                score = result.get(
                    "combined_score", result.get("similarity_score", 0.0)
                )
                similarity_scores.append(score)

            logger.info(f"Retrieved doc IDs: {retrieved_ids}")
            if similarity_scores:
                logger.info(
                    f"Similarity scores: {[f'{s:.3f}' for s in similarity_scores]}"
                )

            # Calculate metrics
            precision = calculate_precision_at_k(retrieved_ids, relevant_doc_ids, k=5)
            recall = calculate_recall_at_k(retrieved_ids, relevant_doc_ids, k=5)
            mrr = calculate_mrr(retrieved_ids, relevant_doc_ids)

            logger.info(f"Precision@5: {precision:.3f}")
            logger.info(f"Recall@5: {recall:.3f}")
            logger.info(f"MRR: {mrr:.3f}")

            strategy_precision.append(precision)
            strategy_recall.append(recall)
            strategy_mrr.append(mrr)
            if similarity_scores:
                strategy_similarity.extend(similarity_scores)

        # Strategy averages
        avg_precision = sum(strategy_precision) / len(strategy_precision)
        avg_recall = sum(strategy_recall) / len(strategy_recall)
        avg_mrr = sum(strategy_mrr) / len(strategy_mrr)
        avg_similarity = (
            sum(strategy_similarity) / len(strategy_similarity)
            if strategy_similarity
            else 0
        )

        logger.info(f"\n{strategy.upper()} STRATEGY RESULTS:")
        logger.info(f"  Average Precision@5: {avg_precision:.3f}")
        logger.info(f"  Average Recall@5: {avg_recall:.3f}")
        logger.info(f"  Average MRR: {avg_mrr:.3f}")
        logger.info(f"  Average Similarity: {avg_similarity:.3f}")

        all_precision.append(avg_precision)
        all_recall.append(avg_recall)
        all_mrr.append(avg_mrr)
        all_similarity_scores.append(avg_similarity)

    # Overall results
    logger.info("\n" + "=" * 70)
    logger.info("OVERALL RESULTS")
    logger.info("=" * 70)

    for i, strategy in enumerate(strategies):
        logger.info(f"\n{strategy}:")
        logger.info(f"  Precision@5: {all_precision[i]:.3f}")
        logger.info(f"  Recall@5: {all_recall[i]:.3f}")
        logger.info(f"  MRR: {all_mrr[i]:.3f}")
        logger.info(f"  Avg Similarity: {all_similarity_scores[i]:.3f}")

    # Best strategy
    best_precision_idx = all_precision.index(max(all_precision))
    logger.info(f"\n🏆 Best Precision: {strategies[best_precision_idx]}")

    logger.info("\n" + "=" * 70)
    logger.info("⚠️  IMPORTANT NOTES:")
    logger.info("=" * 70)
    logger.info("1. This is a MINIMAL test set (only 3 questions)")
    logger.info("2. Ground truth is APPROXIMATE (not human-verified)")
    logger.info("3. Results are INDICATIVE only, not publication-quality")
    logger.info("4. For real accuracy, need 50+ questions with human labels")
    logger.info("=" * 70)


def evaluate_answer_quality():
    """Evaluate generated answer quality (manual inspection required)"""
    logger.info("\n" + "=" * 70)
    logger.info("ANSWER QUALITY EVALUATION")
    logger.info("=" * 70)
    logger.info("⚠️  This requires manual human evaluation")
    logger.info("   Running sample queries for manual inspection...")
    logger.info("=" * 70)

    retriever = HybridRetriever()
    llm_client = LLMClient()

    for test_case in TEST_QUESTIONS[:2]:  # Just first 2 for speed
        question = test_case["question"]
        expected_keywords = test_case["expected_keywords"]

        logger.info(f"\n❓ Question: {question}")
        logger.info(f"Expected keywords: {expected_keywords}")

        # Retrieve context
        results = retriever.search(question, strategy="auto", top_k=3)

        # Build context
        context_chunks = [r.get("document", "") for r in results]
        context = "\n\n".join(context_chunks[:3])

        # Generate answer
        messages = [
            {
                "role": "system",
                "content": f"Answer based on this context:\n\n{context}",
            },
            {"role": "user", "content": question},
        ]

        try:
            answer = llm_client.generate_response(messages)
            logger.info(f"\n💬 Generated Answer:\n{answer}\n")

            # Simple keyword check
            keywords_found = [
                kw for kw in expected_keywords if kw.lower() in answer.lower()
            ]
            logger.info(
                f"✅ Keywords found: {keywords_found} ({len(keywords_found)}/{len(expected_keywords)})"
            )
            logger.info(
                f"📝 Manual inspection needed: Is this answer correct and complete?"
            )

        except Exception as e:
            logger.error(f"❌ Answer generation failed: {e}")

    logger.info("\n" + "=" * 70)


def main():
    """Run accuracy evaluation"""
    logger.info("Starting RAG Accuracy Evaluation...")
    logger.info("⚠️  WARNING: This uses a minimal test set!")
    logger.info("   For production, create a proper evaluation dataset.\n")

    try:
        # Retrieval accuracy
        evaluate_retrieval_accuracy()

        # Answer quality (requires manual inspection)
        logger.info("\n\n")
        evaluate_answer_quality()

        logger.info("\n✅ Evaluation complete!")
        logger.info("\n📝 RECOMMENDATIONS:")
        logger.info("1. Create a larger test set (50-100 questions)")
        logger.info("2. Have humans label relevant documents")
        logger.info("3. Have humans rate answer quality (1-5 scale)")
        logger.info("4. Run weekly to track improvements")

    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
