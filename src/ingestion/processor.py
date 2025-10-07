# src/ingestion/processor.py
from typing import List, Dict, Any
from src.ingestion.loader import DocumentLoader
from src.ingestion.chunker import DocumentChunker
from src.ingestion.embedder import Embedder
from src.knowledge_base.vector_store import VectorStore
from src.knowledge_base.metadata_store import MetadataStore
from loguru import logger
from tqdm import tqdm


class IngestionProcessor:
    """Main ingestion orchestrator"""

    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.metadata_store = MetadataStore()

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single file"""
        logger.info(f"Processing file: {file_path}")

        try:
            # Load document
            document = self.loader.load_file(file_path)

            # Store document metadata
            doc_id = self.metadata_store.store_document(document["metadata"])

            # Chunk document
            chunks = self.chunker.chunk_document(document)

            # Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedder.embed_batch(texts)

            # Store in vector database
            chunk_ids = [chunk["chunk_id"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]

            self.vector_store.add_documents(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids,
            )

            # Store chunk metadata
            for chunk in chunks:
                self.metadata_store.store_chunk(doc_id, chunk)

            logger.info(f"✅ Processed {len(chunks)} chunks from {file_path}")

            return {
                "doc_id": doc_id,
                "chunks": len(chunks),
                "file": file_path,
                "status": "success",
            }

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return {"file": file_path, "error": str(e), "status": "error"}

    def process_text(
        self, text: str, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process raw text"""
        logger.info("Processing raw text")

        try:
            # Create document structure
            document = {
                "content": text,
                "metadata": metadata
                or {"source": "raw_text", "type": "text", "filename": "raw_text"},
            }

            # Store document metadata
            doc_id = self.metadata_store.store_document(document["metadata"])

            # Chunk document
            chunks = self.chunker.chunk_document(document)

            # Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedder.embed_batch(texts)

            # Store in vector database
            chunk_ids = [chunk["chunk_id"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]

            self.vector_store.add_documents(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids,
            )

            # Store chunk metadata
            for chunk in chunks:
                self.metadata_store.store_chunk(doc_id, chunk)

            logger.info(f"✅ Processed {len(chunks)} chunks from raw text")

            return {"doc_id": doc_id, "chunks": len(chunks), "status": "success"}

        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return {"error": str(e), "status": "error"}

    def process_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Process all files in directory"""
        documents = self.loader.load_directory(directory)
        results = []

        for doc in tqdm(documents, desc="Processing documents"):
            result = self.process_file(doc["metadata"]["source"])
            results.append(result)

        success_count = len([r for r in results if r.get("status") == "success"])
        logger.info(f"Processed {success_count}/{len(results)} documents successfully")

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        vector_stats = self.vector_store.get_collection_stats()
        metadata_stats = self.metadata_store.get_stats()

        return {"vector_store": vector_stats, "metadata_store": metadata_stats}
