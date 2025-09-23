from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..schemas.chat import SummarizeIn
from ..memory import SESSIONS
from ..services.llm import answer_stream

router = APIRouter()

@router.post("")
def summarize(payload: SummarizeIn):
    s = SESSIONS.get(payload.session_id)
    if not s.ready or not s.chunks:
        raise HTTPException(400, "no indexed content; upload first")
    parts = []
    for sid, doc in s.docs.items():
        txt = doc["text"]
        parts.append(f"[{sid}] {txt[:600]}")
    prompt = f"Summarize the following documents into a concise {payload.mode} brief with bullet action items.\n\n" + "\n\n".join(parts)
    out = "".join(list(answer_stream(prompt)))
    return JSONResponse({"summary": out, "sources": list(s.docs.keys())})
