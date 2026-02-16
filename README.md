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
2. Deploy LLM, Embedding, vector db in EC2.
3. For Front End: Amplify.
4. BE: AppRunner (Optional).
5. Configure logs.

# FastAPI Endpoints
1. `POST /document/upload-index`
   * Accepts a `.json` file, embeds content, and stores vectors in Qdrant.
2. `POST /document/doc-chat`
   * Accepts `user_query` and returns an answer grounded on indexed documents.

# Streamlit Frontend
A Streamlit app is available in `streamlit_app.py` with:
* Upload UI for `/document/upload-index`.
* Chat UI for `/document/doc-chat`.
* Configurable FastAPI base URL from the sidebar.

## Run locally
```bash
uv sync
uv run fastapi dev main.py --port 8000
uv run streamlit run streamlit_app.py --server.port 8501
```

# CI/CD & Deployment
* The entire deployment process is automatic using GitHub Actions.
* **Trigger**: On every git push to the main branch.
* **Workflow**:
  1. SSH into the EC2 instance.
  2. Run `docker-compose up -d` to pull and start backend and Qdrant containers.
