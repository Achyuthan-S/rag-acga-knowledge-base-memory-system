#!/usr/bin/env python3
"""Test Gemini API integration"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
from config.settings import get_settings


def test_gemini_connection():
    """Test basic Gemini API connection"""
    print("=" * 60)
    print("Testing Gemini API Connection")
    print("=" * 60)

    settings = get_settings()

    print(f"\nProvider: {settings.llm_provider}")
    print(f"LLM Model: {settings.llm_model}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"Embedding Dimension: {settings.embedding_dimension}")

    # Check API key
    if settings.llm_provider.lower() == "gemini":
        if (
            not settings.gemini_api_key
            or settings.gemini_api_key == "your_gemini_api_key_here"
        ):
            print("\n❌ ERROR: GEMINI_API_KEY not set in .env file")
            print("\n📝 To get a FREE Gemini API key:")
            print("   1. Visit: https://aistudio.google.com/app/apikey")
            print("   2. Sign in with Google (no credit card needed)")
            print("   3. Click 'Create API key'")
            print("   4. Copy the key and add to .env file:")
            print("      GEMINI_API_KEY=AIzaSy...")
            return False
        print(f"\n✅ Gemini API Key found: {settings.gemini_api_key[:10]}...")

    print("\n" + "-" * 60)
    print("Testing Embedding Generation...")
    print("-" * 60)

    try:
        from src.ingestion.embedder import Embedder

        embedder = Embedder()
        test_text = "This is a test sentence for embedding."

        print(f"\nGenerating embedding for: '{test_text}'")
        embedding = embedder.embed_text(test_text)

        print(f"✅ Embedding generated successfully!")
        print(f"   Dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")

    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False

    print("\n" + "-" * 60)
    print("Testing LLM Response Generation...")
    print("-" * 60)

    try:
        from src.llm.client import LLMClient

        llm = LLMClient()
        messages = [
            {"role": "user", "content": "Say 'Hello from Gemini!' and nothing else."}
        ]

        print("\nSending test message to LLM...")
        response = llm.generate_response(messages)

        print(f"✅ LLM response received!")
        print(f"   Response: {response}")

    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour Gemini integration is working correctly!")
    print("\nNext steps:")
    print("  1. Start the API: ./.venv/bin/uvicorn api.main:app --reload --port 8000")
    print("  2. Start the UI: ./.venv/bin/streamlit run ui/app.py")
    print("  3. Ingest data: ./.venv/bin/python scripts/ingest_sample_data.py")

    return True


if __name__ == "__main__":
    try:
        success = test_gemini_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
