# src/llm/client.py
from typing import List, Dict, Optional
from loguru import logger
from config.settings import get_settings


class LLMClient:
    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.llm_provider.lower()

        if self.provider == "openai":
            from openai import OpenAI

            self.client = OpenAI(api_key=self.settings.openai_api_key)
            logger.info("LLM client initialized with OpenAI")
        elif self.provider == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=self.settings.gemini_api_key)
            self.client = genai
            logger.info("LLM client initialized with Gemini")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            if self.provider == "openai":
                response = self.client.embeddings.create(
                    model=self.settings.embedding_model, input=text
                )
                return response.data[0].embedding
            elif self.provider == "gemini":
                result = self.client.embed_content(
                    model=self.settings.embedding_model,
                    content=text,
                    task_type="retrieval_document",
                )
                return result["embedding"]
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            if self.provider == "openai":
                response = self.client.embeddings.create(
                    model=self.settings.embedding_model, input=texts
                )
                return [data.embedding for data in response.data]
            elif self.provider == "gemini":
                # Gemini batch processing
                embeddings = []
                for text in texts:
                    result = self.client.embed_content(
                        model=self.settings.embedding_model,
                        content=text,
                        task_type="retrieval_document",
                    )
                    embeddings.append(result["embedding"])
                return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate response from LLM"""
        try:
            if self.provider == "openai":
                # OpenAI implementation
                formatted_messages = []
                if system_prompt:
                    formatted_messages.append(
                        {"role": "system", "content": system_prompt}
                    )
                formatted_messages.extend(messages)

                response = self.client.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=formatted_messages,
                    temperature=temperature or self.settings.llm_temperature,
                    max_tokens=max_tokens or self.settings.llm_max_tokens,
                )
                return response.choices[0].message.content

            elif self.provider == "gemini":
                # Gemini implementation
                model = self.client.GenerativeModel(
                    model_name=f"models/{self.settings.llm_model}",
                    system_instruction=system_prompt,
                )

                # Convert messages to Gemini format
                chat = model.start_chat(history=[])

                # Build conversation history
                for msg in messages[:-1]:  # All but last message
                    if msg["role"] == "user":
                        chat.send_message(msg["content"])

                # Send final message and get response
                response = chat.send_message(
                    messages[-1]["content"],
                    generation_config={
                        "temperature": temperature or self.settings.llm_temperature,
                        "max_output_tokens": max_tokens or self.settings.llm_max_tokens,
                    },
                )
                return response.text

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
