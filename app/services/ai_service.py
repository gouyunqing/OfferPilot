from __future__ import annotations
import uuid
import json
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.wallet import AiAnswerCache
from app.models.question import Question
from app.models.user import User
from app.config import settings


def _cache_id() -> str:
    return "ai_" + uuid.uuid4().hex[:9]


class AiService:
    @staticmethod
    async def stream_answer(
        db: AsyncSession, user_id: str, question_id: str
    ) -> AsyncGenerator[str, None]:
        # Check member
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user or not user.is_member:
            error_event = f"event: error\ndata: {json.dumps({'code': 40003, 'message': '需要会员'})}\n\n"
            yield error_event
            return

        q = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
        if not q:
            yield f"event: error\ndata: {json.dumps({'code': 40004, 'message': '题目不存在'})}\n\n"
            return

        request_id = "ai_req_" + uuid.uuid4().hex[:8]
        yield f"event: start\ndata: {json.dumps({'request_id': request_id})}\n\n"

        # TODO: call DeepSeek / Qianwen API with streaming
        mock_answer = f"这是关于「{q.content[:30]}」的 AI 参考答案（模拟流式输出）。"
        for chunk in [mock_answer[:20], mock_answer[20:]]:
            yield f"event: chunk\ndata: {json.dumps({'content': chunk})}\n\n"

        yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'total_tokens': 100})}\n\n"

        # Cache answer
        cache = (await db.execute(
            select(AiAnswerCache).where(AiAnswerCache.question_id == question_id)
        )).scalar_one_or_none()
        if not cache:
            db.add(AiAnswerCache(id=_cache_id(), question_id=question_id, content=mock_answer))
            await db.commit()

    @staticmethod
    async def get_cached_answer(db: AsyncSession, user_id: str, question_id: str) -> Optional[dict]:
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user or not user.is_member:
            raise HTTPException(status_code=403, detail={"code": 40003, "message": "需要会员"})

        cache = (await db.execute(
            select(AiAnswerCache).where(AiAnswerCache.question_id == question_id)
        )).scalar_one_or_none()
        if not cache:
            return None
        return {
            "question_id": cache.question_id,
            "content": cache.content,
            "generated_at": cache.generated_at,
        }
