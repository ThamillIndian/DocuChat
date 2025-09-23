# NotebookLM Pipeline Backend (Stateless MVP)

FastAPI backend for a NotebookLM-like pipeline. No DB, no auth. In-memory session, uploads, RAG chat (SSE), Summarize-All.

## Run
```bash
pip install -r <(echo fastapi uvicorn[standard] python-multipart pydantic)
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `POST /session/new` → `{session_id}`
- `DELETE /session/{id}`
- `POST /session/{id}/upload` (multipart files[])
- `POST /chat/stream` (SSE)
- `POST /summarize`
- `GET /healthz`
