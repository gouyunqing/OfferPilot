from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NoteUpsertRequest(BaseModel):
    content: str


class NoteResponse(BaseModel):
    id: str
    question_id: str
    content: str
    updated_at: datetime
