#!/usr/bin/env python3
# scripts/setup_databases.py
"""
Setup script to initialize all databases and create necessary schemas
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from config.settings import get_settings
from src.knowledge_base.vector_store import VectorStore
from src.knowledge_base.graph_store import GraphStore
import redis
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def setup_vector_store():
    """Initialize ChromaDB vector store"""
    try:
        logger.info("Setting up vector store...")
        vector_store = VectorStore()
        stats = vector_store.get_collection_stats()
        logger.info(f"Vector store initialized with {stats['count']} documents")
        return True
    except Exception as e:
        logger.error(f"Failed to setup vector store: {e}")
        return False


def setup_graph_store():
    """Initialize Neo4j graph store"""
    try:
        logger.info("Setting up graph store...")
        graph_store = GraphStore()

        # Test connection by getting stats
        stats = graph_store.get_graph_stats()
        logger.info(
            f"Graph store initialized with {stats['nodes']} nodes and {stats['relationships']} relationships"
        )

        graph_store.close()
        return True
    except Exception as e:
        logger.error(f"Failed to setup graph store: {e}")
        return False


def setup_postgres():
    """Initialize PostgreSQL with pgvector extension"""
    try:
        logger.info("Setting up PostgreSQL...")
        settings = get_settings()

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = conn.cursor()

        # Create pgvector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                metadata JSONB,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create index on embedding
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx 
            ON documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)

        cursor.close()
        conn.close()

        logger.info("PostgreSQL setup completed")
        return True

    except Exception as e:
        logger.error(f"Failed to setup PostgreSQL: {e}")
        return False


def setup_redis():
    """Initialize Redis cache"""
    try:
        logger.info("Setting up Redis cache...")
        settings = get_settings()

        r = redis.Redis(
            host=settings.redis_host, port=settings.redis_port, decode_responses=True
        )

        # Test connection
        r.ping()

        # Set a test key
        r.set("rag_system:initialized", "true")
        r.expire("rag_system:initialized", 3600)  # Expire in 1 hour

        logger.info("Redis setup completed")
        return True

    except Exception as e:
        logger.error(f"Failed to setup Redis: {e}")
        return False


def main():
    """Main setup function"""
    logger.info("Starting database setup...")

    success_count = 0
    total_services = 4

    # Setup each service
    if setup_vector_store():
        success_count += 1

    if setup_graph_store():
        success_count += 1

    if setup_postgres():
        success_count += 1

    if setup_redis():
        success_count += 1

    # Summary
    logger.info(
        f"Setup completed: {success_count}/{total_services} services initialized successfully"
    )

    if success_count == total_services:
        logger.info("✅ All databases setup successfully!")
        return True
    else:
        logger.warning(
            f"⚠️ {total_services - success_count} services failed to initialize"
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
