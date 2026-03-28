from pydantic import BaseModel
from typing import Optional, List


class Company(BaseModel):
    id: str
    name: str
    logo: str
    priority: int


class Position(BaseModel):
    id: str
    name: str
    category: str


class Round(BaseModel):
    id: str
    name: str


class CompanyStats(BaseModel):
    company: Company
    total_questions: int
    bagu_count: int
    leetcode_count: int
    latest_question_at: Optional[str] = None
