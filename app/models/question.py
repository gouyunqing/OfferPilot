from __future__ import annotations
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.database import Base
import enum


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploader_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False)
    position_id: Mapped[str] = mapped_column(String(50), ForeignKey("positions.id"), nullable=False)
    recruit_type: Mapped[str] = mapped_column(String(20), nullable=False)
    round: Mapped[str] = mapped_column(String(20), nullable=False)
    interview_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    interview_quarter: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    leetcode_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    leetcode_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="approved")

    confirm_count: Mapped[int] = mapped_column(Integer, default=0)
    reward_total: Mapped[float] = mapped_column(Float, default=0.0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    favorite_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class QuestionCompany(Base):
    __tablename__ = "question_companies"

    question_id: Mapped[str] = mapped_column(String(32), ForeignKey("questions.id"), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(50), ForeignKey("companies.id"), primary_key=True)
