from fastapi import FastAPI
from core.routers import document_index, text_embed, document_chat

app = FastAPI()


app.include_router(document_index.router)
app.include_router(text_embed.router)
app.include_router(document_chat.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}