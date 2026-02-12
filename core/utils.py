import requests
from typing import List
from .config.settings import Settings

settings = Settings()


def get_text_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Calls the custom EC2 FastAPI endpoint to get embeddings.
    Endpoint: /document/embed
    """
    url = settings.embedding_service_url
    
    payload = {
        "sentences": texts
    }
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()["embeddings"]
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to embedding service: {e}")
        raise


def generate_text(prompt):
    payload = {
        "model": settings.llm_model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(settings.llm_api_url, json=payload)
    return response.json().get("response")

if __name__ == "__main__":
    response = get_text_embeddings(["Hello"])
    print(response)