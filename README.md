
# Architecture Diagram
[TODO]

# The Technical Stack
* LLM: `Qwen-0.6B`
* Embedding Model: `BAAI/bge-small-en-v1.5`.
* Vector Database: `Qdrant` (self-hosted).
* Backend: `FastAPI`
* Frontend: `Streamlit` 
* CI/CD: `GitHub Actions`

# Infrastructure Setup
1. Create an EC2 Instance.
2. Deploy LLM, Embedding, vector db in EC2
3. For Front End: Amplify
4. BE:  AppRunner (Optional)
5. Config logs

# FastAPI Endpoints
1. POST /index:
    >Accepts a file (PDF/TXT), chunks the text, generates embeddings using bge-small, and stores them in Qdrant.
2. POST /chat:
    >Accepts a user query, performs a similarity search in Qdrant, and sends the context + query to the Qwen model for a response.

# The User Interface:
>Basic web UI that interacts with the FastAPI backend.

**Features**: 
* A file upload widget and a chat window.

# CI/CD & Deployment
* The entire deployment process is automatic using GitHub Actions.
* **Trigger**: On every git push to the main branch.\
**Workflow**:
    Deploy: GitHub Actions to:
    1. SSH into the EC2 instance.
    2. Run docker-compose up -d to pull and start the Backend, and Qdrant containers.
