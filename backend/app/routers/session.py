from fastapi import APIRouter
from ..memory import SESSIONS
from ..schemas.session import NewSessionOut

router = APIRouter()

@router.post("/new", response_model=NewSessionOut)
def new_session():
    return {"session_id": SESSIONS.new()}

@router.delete("/{session_id}")
def kill_session(session_id: str):
    SESSIONS.delete(session_id)
    return {"ok": True}
