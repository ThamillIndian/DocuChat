import time, uuid
from typing import Dict, Any, List
from fastapi import HTTPException
from .config import settings

class Session:
    def __init__(self):
        self.created = time.time()
        self.docs: Dict[str, Dict[str, Any]] = {}
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Dict[str, list] = {}
        self.ready = False

class SessionStore:
    def __init__(self, ttl: int):
        self.ttl = ttl
        self._store: Dict[str, Session] = {}

    def new(self) -> str:
        sid = str(uuid.uuid4())
        self._store[sid] = Session()
        return sid

    def get(self, sid: str) -> Session:
        s = self._store.get(sid)
        if not s: raise HTTPException(404, "session not found")
        if time.time() - s.created > self.ttl:
            self.delete(sid)
            raise HTTPException(410, "session expired")
        return s

    def delete(self, sid: str):
        self._store.pop(sid, None)

SESSIONS = SessionStore(settings.session_ttl)
