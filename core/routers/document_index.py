from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
import time
import json
import logging

from typing import List, Dict, Any
from pydantic import BaseModel

from core.config.settings import Settings
from core.database.qdrant_client import QdrantManager
from core.database.document_store import DocumentStore
from core.services.embedding_service import EmbeddingService
from core.models.document import Document, DocumentMetadata, DocumentType


router = APIRouter(prefix="/document")

settings = Settings()

qdrant_manager = QdrantManager(settings)
embedding_service = EmbeddingService(settings)
document_store = DocumentStore(qdrant_manager, settings)

qdrant_manager.initialize_collection()
logger = logging.getLogger(__name__)
     

# Helper Functions:

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ingest_documents.log')
        ]
    )

async def ingest_documents_batch(
    documents: List[Document],
    document_store: DocumentStore,
    embedding_service: EmbeddingService,
) -> Dict[str, Any]:
    start_time = time.time()
    
    contents = [doc.content for doc in documents]
    embedding_results = await embedding_service.create_embeddings_batch(contents)
    
    ingestion_results = []
    total_tokens = 0
    total_chunks = 0
    
    for i, (document, embedding_result) in enumerate(zip(documents, embedding_results)):
        chunk_embeddings = None
        if len(document.content.split()) > 500:
            chunks = embedding_service.chunk_text(document.content)
            if len(chunks) > 1:
                document.chunks = chunks
                chunk_embedding_results = await embedding_service.create_embeddings_batch(chunks)
                chunk_embeddings = [result.embedding for result in chunk_embedding_results]
        
        result = document_store.ingest_document(
            document=document,
            embedding=embedding_result.embedding,
            chunk_embeddings=chunk_embeddings
        )
        
        ingestion_results.append(result)
        total_tokens += embedding_result.token_count
        total_chunks += result.chunk_count or 0
        
        if result.success:
            logger.info(f"{document.metadata.title or document.id}")
        else:
            logger.error(f"{document.metadata.title or document.id}: {result.message}")
    
    processing_time = time.time() - start_time
    successful = sum(1 for r in ingestion_results if r.success)
    
    return {
        "total": len(documents),
        "successful": successful,
        "failed": len(documents) - successful,
        "total_tokens": total_tokens,
        "total_chunks": total_chunks,
        "processing_time": processing_time,
        "results": ingestion_results
    }


def load_documents_from_json(file_path: Path) -> List[Dict[str, Any]]:
    """Load documents from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both single document and array of documents
    if isinstance(data, dict):
        return [data]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("JSON file must contain a document object or array of documents")
	

class IngestionResponse(BaseModel):
    total_processed: int
    successful: int
    failed: int
    total_chunks: int
    processing_time: float

@router.post("/upload-index", response_model=IngestionResponse)
async def upload_and_index(
    file: UploadFile = File(...), 
    batch_size: int = 10
):
    # 1. Validate File Type
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only .json files are supported.")

    try:
        # 2. Read and Parse JSON content
        contents = await file.read()
        raw_documents = json.loads(contents)
        if isinstance(raw_documents, dict):
            raw_documents = [raw_documents]
        
        # 3. Transform to Document Objects
        documents = [
            Document(
                content=doc["content"],
                metadata=DocumentMetadata(**doc.get("metadata", {}))
            ) for doc in raw_documents
        ]

        # 4. Processing logic (Same as before)
        metrics = {
            "total_processed": len(documents),
            "successful": 0, "failed": 0, "total_tokens": 0, 
            "total_chunks": 0, "processing_time": 0.0
        }

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_res = await ingest_documents_batch(
                batch, document_store, embedding_service
            )
            
            # Aggregate metrics
            metrics["successful"] += batch_res["successful"]
            metrics["failed"] += batch_res["failed"]
            metrics["total_tokens"] += batch_res.get("total_tokens", 0)
            metrics["total_chunks"] += batch_res.get("total_chunks", 0)
            metrics["processing_time"] += batch_res.get("processing_time", 0)

        return metrics

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")
    except Exception as e:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()
