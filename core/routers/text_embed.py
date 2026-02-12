from fastapi import APIRouter
from sentence_transformers import SentenceTransformer
from ..models.text import TextData

router = APIRouter(prefix="/document")

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

@router.post("/embed")
async def get_embeddings(data: TextData):
    embeddings = model.encode(data.sentences)
    return {"embeddings": embeddings.tolist()}
