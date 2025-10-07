# config/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    gemini_api_key: str = ""
    llm_provider: str = "gemini"  # "openai" or "gemini"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password123"

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "rag_user"
    postgres_password: str = "rag_password"
    postgres_db: str = "rag_db"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    # Embedding
    embedding_model: str = "models/text-embedding-004"  # Gemini embedding model
    embedding_dimension: int = 768  # Gemini embedding dimension

    # LLM
    llm_model: str = "gemini-1.5-flash"  # or "gemini-1.5-pro"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma_db"

    # App Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_retrieval_results: int = 10
    log_level: str = "INFO"

    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
