from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AiAnswerRequest(BaseModel):
    question_id: str


class AiAnswerHistoryResponse(BaseModel):
    question_id: str
    content: str
    generated_at: datetime
