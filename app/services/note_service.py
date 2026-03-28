from __future__ import annotations
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from app.models.social import Note
from app.schemas.note import NoteUpsertRequest


def _note_id() -> str:
    return "note_" + uuid.uuid4().hex[:9]


class NoteService:
    @staticmethod
    async def upsert_note(db: AsyncSession, question_id: str, user_id: str, body: NoteUpsertRequest) -> dict:
        note = (await db.execute(
            select(Note).where(Note.user_id == user_id, Note.question_id == question_id)
        )).scalar_one_or_none()
        if note:
            note.content = body.content
        else:
            note = Note(id=_note_id(), user_id=user_id, question_id=question_id, content=body.content)
            db.add(note)
        await db.flush()
        return {
            "id": note.id,
            "question_id": note.question_id,
            "content": note.content,
            "updated_at": note.updated_at,
        }

    @staticmethod
    async def get_note(db: AsyncSession, question_id: str, user_id: str) -> Optional[dict]:
        note = (await db.execute(
            select(Note).where(Note.user_id == user_id, Note.question_id == question_id)
        )).scalar_one_or_none()
        if not note:
            return None
        return {
            "id": note.id,
            "question_id": note.question_id,
            "content": note.content,
            "updated_at": note.updated_at,
        }

    @staticmethod
    async def delete_note(db: AsyncSession, question_id: str, user_id: str) -> None:
        note = (await db.execute(
            select(Note).where(Note.user_id == user_id, Note.question_id == question_id)
        )).scalar_one_or_none()
        if not note:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "笔记不存在"})
        await db.delete(note)

    @staticmethod
    async def get_all_notes(db: AsyncSession, user_id: str, page: int, page_size: int) -> dict:
        stmt = select(Note).where(Note.user_id == user_id).order_by(Note.updated_at.desc())
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(stmt.offset(offset).limit(page_size))
        notes = result.scalars().all()
        return {
            "items": [
                {
                    "id": n.id,
                    "question_id": n.question_id,
                    "content": n.content,
                    "updated_at": n.updated_at,
                }
                for n in notes
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + len(notes) < total,
        }
