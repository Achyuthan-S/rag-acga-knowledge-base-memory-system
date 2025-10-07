# src/ingestion/embedder.py
from typing import List
from config.settings import get_settings
from loguru import logger
import time


class Embedder:
    """Generate embeddings for text"""

    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.llm_provider.lower()
        self.model = self.settings.embedding_model

        if self.provider == "openai":
            from openai import OpenAI

            self.client = OpenAI(api_key=self.settings.openai_api_key)
        elif self.provider == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=self.settings.gemini_api_key)
            self.client = genai

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        try:
            if self.provider == "openai":
                response = self.client.embeddings.create(input=text, model=self.model)
                return response.data[0].embedding
            elif self.provider == "gemini":
                result = self.client.embed_content(
                    model=self.model, content=text, task_type="retrieval_document"
                )
                return result["embedding"]
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            try:
                if self.provider == "openai":
                    response = self.client.embeddings.create(
                        input=batch, model=self.model
                    )
                    batch_embeddings = [data.embedding for data in response.data]
                    embeddings.extend(batch_embeddings)
                elif self.provider == "gemini":
                    # Gemini processes one at a time for now
                    for text in batch:
                        result = self.client.embed_content(
                            model=self.model,
                            content=text,
                            task_type="retrieval_document",
                        )
                        embeddings.append(result["embedding"])

                logger.info(f"Generated embeddings for batch {i // batch_size + 1}")
                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error in batch {i}: {e}")
                raise

        return embeddings
