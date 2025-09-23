from pydantic import BaseModel
from typing import Optional

class ChatIn(BaseModel):
    session_id: str
    message: str
    k: Optional[int] = 8
    max_ctx: Optional[int] = 6000

class SummarizeIn(BaseModel):
    session_id: str
    mode: str | None = "executive"
