from fastapi import APIRouter

router = APIRouter(prefix="/document")

@router.get("/index")
def health_index():
    return "Indexing Document"