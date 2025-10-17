# src/ingestion/chunker.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import hashlib
from config.settings import get_settings
from loguru import logger


class DocumentChunker:
    """Chunk documents into smaller pieces"""

    def __init__(self):
        self.settings = get_settings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk a document"""
        content = document["content"]
        metadata = document.get("metadata", {})

        chunks = self.text_splitter.split_text(content)

        chunked_docs = []
        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_chunk_id(chunk, metadata.get("source", ""), i)

            chunk_metadata = metadata.copy()
            chunk_metadata.update(
                {"chunk_index": i, "total_chunks": len(chunks), "chunk_id": chunk_id}
            )

            chunked_docs.append(
                {"chunk_id": chunk_id, "text": chunk, "metadata": chunk_metadata}
            )

        logger.info(f"Created {len(chunked_docs)} chunks from document")
        return chunked_docs

    def _generate_chunk_id(self, text: str, source: str, index: int) -> str:
        """Generate unique chunk ID"""
        content = f"{source}_{index}_{text[:100]}"
        return hashlib.md5(content.encode()).hexdigest()

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk multiple documents"""
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks
