# src/knowledge_base/metadata_store.py
import psycopg2
from psycopg2.extras import Json
from typing import Dict, Any, List, Optional
from datetime import datetime
from config.settings import get_settings
from loguru import logger


class MetadataStore:
    """PostgreSQL metadata store"""

    def __init__(self):
        self.settings = get_settings()
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.settings.postgres_host,
                port=self.settings.postgres_port,
                user=self.settings.postgres_user,
                password=self.settings.postgres_password,
                database=self.settings.postgres_db,
            )
            logger.info("Connected to metadata store")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _create_tables(self):
        """Create necessary tables"""
        cursor = self.conn.cursor()

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(255) UNIQUE NOT NULL,
                title VARCHAR(500),
                source TEXT,
                content_type VARCHAR(50),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

        # Chunks table - create after documents table is committed
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                chunk_id VARCHAR(255) UNIQUE NOT NULL,
                doc_id VARCHAR(255),
                chunk_index INTEGER,
                content TEXT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source)"
        )

        self.conn.commit()
        cursor.close()

    def store_document(self, metadata: Dict[str, Any]) -> str:
        """Store document metadata"""
        cursor = self.conn.cursor()

        doc_id = (
            metadata.get("source", "") + "_" + str(int(datetime.utcnow().timestamp()))
        )

        cursor.execute(
            """
            INSERT INTO documents (doc_id, title, source, content_type, metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (doc_id) DO UPDATE SET 
                updated_at = CURRENT_TIMESTAMP,
                metadata = EXCLUDED.metadata
            RETURNING doc_id
        """,
            (
                doc_id,
                metadata.get("filename", ""),
                metadata.get("source", ""),
                metadata.get("type", ""),
                Json(metadata),
            ),
        )

        result = cursor.fetchone()
        self.conn.commit()
        cursor.close()

        return result[0] if result else doc_id

    def store_chunk(self, doc_id: str, chunk: Dict[str, Any]):
        """Store chunk metadata"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO chunks (chunk_id, doc_id, chunk_index, content, metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (chunk_id) DO NOTHING
        """,
            (
                chunk["chunk_id"],
                doc_id,
                chunk["metadata"].get("chunk_index", 0),
                chunk["text"],
                Json(chunk["metadata"]),
            ),
        )

        self.conn.commit()
        cursor.close()

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE doc_id = %s", (doc_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return {
                "id": result[0],
                "doc_id": result[1],
                "title": result[2],
                "source": result[3],
                "content_type": result[4],
                "metadata": result[5],
                "created_at": result[6],
                "updated_at": result[7],
            }
        return None

    def get_chunks_by_doc_id(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM chunks 
            WHERE doc_id = %s 
            ORDER BY chunk_index
        """,
            (doc_id,),
        )
        results = cursor.fetchall()
        cursor.close()

        return [
            {
                "id": row[0],
                "chunk_id": row[1],
                "doc_id": row[2],
                "chunk_index": row[3],
                "content": row[4],
                "metadata": row[5],
                "created_at": row[6],
            }
            for row in results
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chunks")
        chunk_count = cursor.fetchone()[0]

        cursor.close()

        return {"documents": doc_count, "chunks": chunk_count}

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
