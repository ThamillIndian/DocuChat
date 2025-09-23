from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid

from ..memory import SESSIONS
from ..config import settings
from ..services.extract import read_text_any
from ..services.asr_sarvam import transcribe
from ..services.chunk import chunk_text
from ..services.embed import embed_text

router = APIRouter()

@router.post("/{session_id}/upload")
async def upload(session_id: str, files: List[UploadFile] = File(...)):
    s = SESSIONS.get(session_id)
    if not files: raise HTTPException(400, "no files")
    total = sum((f.size or 0) for f in files if hasattr(f, "size"))
    if total and total > settings.max_file_mb * 1024 * 1024:
        raise HTTPException(400, "payload too large")

    added = []
    for f in files:
        b = await f.read()
        mime = f.content_type or "application/octet-stream"
        name = f.filename or "file"
        if mime.startswith(("audio/","video/")) or name.lower().endswith((".mp3",".mp4",".m4a",".wav",".mov",".mkv")):
            tr = transcribe(b, name, mime)
            text = tr["text"]; meta = {"type":"av","sarvam":True, **tr.get("meta",{})}
        else:
            doc = read_text_any(b, name, mime)
            text = doc["text"]; meta = {"type":"doc", **doc["meta"]}
        source_id = str(uuid.uuid4())
        s.docs[source_id] = {"text": text, "meta": meta}
        for i, piece in enumerate(chunk_text(text, size=800)):
            cid = str(uuid.uuid4())
            s.chunks.append({"id": cid, "text": piece, "source_id": source_id, "span": {"chunk": i}})
            s.embeddings[cid] = embed_text(piece)
        added.append({"source_id": source_id, "filename": name, "len": len(text)})
    s.ready = True
    return {"added": added, "total_chunks": len(s.chunks)}
