from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .routers import session, upload, chat, summarize

app = FastAPI(title="NotebookLM Pipeline Backend (Stateless MVP)", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"])

app.include_router(session.router,  prefix="/session",  tags=["session"])
app.include_router(upload.router,   prefix="/session",  tags=["upload"])   # /session/{id}/upload
app.include_router(chat.router,     prefix="/chat",     tags=["chat"])
app.include_router(summarize.router, prefix="/summarize", tags=["summarize"])

@app.get("/healthz")
def healthz():
    return {"ok": True}
