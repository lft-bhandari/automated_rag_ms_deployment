from fastapi import APIRouter
from core.services.response_generator import ResponseGenerator
from core.services.search_engine import HybridSearchEngine
from core.database.qdrant_client import QdrantManager
from core.database.document_store import DocumentStore
from core.services.embedding_service import EmbeddingService

from core.config.settings import Settings

settings = Settings()        
# Initialize services
qdrant_manager = QdrantManager(settings)
embedding_service = EmbeddingService(settings)
router = APIRouter(prefix="/document")

response_generator = ResponseGenerator(settings)
search_engine = HybridSearchEngine(qdrant_manager=qdrant_manager,
                                   embedding_service=embedding_service,
                                   settings=settings)

@router.post("/doc-chat")
async def doc_chat(user_query:str):
    
    search_results = await search_engine.search(
                query=user_query,
                limit=settings.max_sources_per_response,
                vector_weight=settings.default_vector_weight,
                keyword_weight=settings.default_keyword_weight,
            )
    response = await response_generator.generate_response(query=user_query, search_results=search_results)

    return response["response"]
    

