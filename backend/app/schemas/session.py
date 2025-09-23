from pydantic import BaseModel

class NewSessionOut(BaseModel):
    session_id: str
