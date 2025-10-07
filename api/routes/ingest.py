# api/routes/ingest.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any
from loguru import logger
from src.ingestion.processor import IngestionProcessor
import tempfile
import os

router = APIRouter()
processor = IngestionProcessor()


class IngestResponse(BaseModel):
    message: str
    documents_processed: int
    chunks_created: int
    metadata: Dict[str, Any]


@router.post("/document", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document into the knowledge base"""
    try:
        import tempfile
        import os

        logger.info(f"Received file: {file.filename}")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f"_{file.filename}"
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Process the file
            result = processor.process_file(temp_file_path)

            if result.get("status") == "success":
                return IngestResponse(
                    message=f"Document {file.filename} processed successfully",
                    documents_processed=1,
                    chunks_created=result.get("chunks", 0),
                    metadata={
                        "filename": file.filename,
                        "file_size": len(content),
                        "content_type": file.content_type,
                        "doc_id": result.get("doc_id"),
                    },
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Processing failed: {result.get('error', 'Unknown error')}",
                )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TextIngestRequest(BaseModel):
    text: str
    metadata: Dict[str, Any] = {}


@router.post("/text", response_model=IngestResponse)
async def ingest_text(request: TextIngestRequest):
    """Ingest raw text into the knowledge base"""
    try:
        logger.info(f"Received text of length: {len(request.text)}")

        # Process the text
        result = processor.process_text(request.text, request.metadata)

        if result.get("status") == "success":
            return IngestResponse(
                message="Text processed successfully",
                documents_processed=1,
                chunks_created=result.get("chunks", 0),
                metadata={
                    **request.metadata,
                    "doc_id": result.get("doc_id"),
                    "text_length": len(request.text),
                },
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Processing failed: {result.get('error', 'Unknown error')}",
            )

    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_ingestion_stats():
    """Get ingestion statistics"""
    try:
        stats = processor.get_stats()
        return {
            "total_documents": stats["metadata_store"]["documents"],
            "total_chunks": stats["metadata_store"]["chunks"],
            "vector_store_count": stats["vector_store"]["count"],
            "status": "healthy",
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
