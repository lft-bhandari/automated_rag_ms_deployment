import requests
from typing import List
from sentence_transformers import SentenceTransformer
from .config.settings import Settings

settings = Settings()

model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def get_text_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Calls the custom EC2 FastAPI endpoint to get embeddings.
    Endpoint: /document/embed
    """
    # url = settings.embedding_service_url
    
    # payload = {
    #     "sentences": texts
    # }
    
    # headers = {
    #     "accept": "application/json",
    #     "Content-Type": "application/json"
    # }

    # try:
    #     response = requests.post(
    #         url,
    #         json=payload,
    #         headers=headers
    #     )
    #     response.raise_for_status()
        
    #     return response.json()["embeddings"]
        
    # except requests.exceptions.RequestException as e:
    #     print(f"Error connecting to embedding service: {e}")
    #     raise
    embeddings = model.encode(texts)
    return embeddings


def generate_text(model,prompt):

    combined_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in prompt])
    payload = {
        "model": model,
        "prompt": combined_prompt,
        "stream": False
    }
    response = requests.post(settings.llm_api_url, json=payload)
    # print(response.json().get("response"))
    # final_response["answer"] = response.json().get("response")
    return response.json()

if __name__ == "__main__":
    response = get_text_embeddings(["Hello"])
    print(response)