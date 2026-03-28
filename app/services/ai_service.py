from __future__ import annotations
import uuid
import json
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from openai import AsyncOpenAI

from app.models.wallet import AiAnswerCache
from app.models.question import Question
from app.models.user import User
from app.config import settings

SYSTEM_PROMPT = (
    "你是 OfferPilot 的 AI 面试助手，专注于互联网大厂面试题解析。"
    "请给出结构清晰、重点突出的参考答案。先给出核心要点，再展开详细解释。"
    "如果是八股文题目，请结合实际应用场景回答；如果是算法题，请给出思路和关键代码。"
)


def _cache_id() -> str:
    return "ai_" + uuid.uuid4().hex[:9]


def _get_ai_client() -> tuple[AsyncOpenAI, str]:
    """根据配置返回 (client, model_name)"""
    if settings.AI_PROVIDER == "deepseek":
        client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        return client, "deepseek-chat"
    else:
        client = AsyncOpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
        )
        return client, settings.DASHSCOPE_MODEL


class AiService:
    @staticmethod
    async def stream_answer(
        db: AsyncSession, user_id: str, question_id: str
    ) -> AsyncGenerator[str, None]:
        # 检查会员
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user or not user.is_member:
            yield f"event: error\ndata: {json.dumps({'code': 40003, 'message': '需要会员'}, ensure_ascii=False)}\n\n"
            return

        q = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
        if not q:
            yield f"event: error\ndata: {json.dumps({'code': 40004, 'message': '题目不存在'}, ensure_ascii=False)}\n\n"
            return

        # 检查缓存
        cached = (await db.execute(
            select(AiAnswerCache).where(AiAnswerCache.question_id == question_id)
        )).scalar_one_or_none()
        if cached:
            request_id = "ai_cached_" + uuid.uuid4().hex[:8]
            yield f"event: start\ndata: {json.dumps({'request_id': request_id, 'cached': True})}\n\n"
            # 分块返回缓存内容（模拟流式体验）
            chunk_size = 60
            for i in range(0, len(cached.content), chunk_size):
                yield f"event: chunk\ndata: {json.dumps({'content': cached.content[i:i+chunk_size]}, ensure_ascii=False)}\n\n"
            yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'total_tokens': 0, 'cached': True})}\n\n"
            return

        request_id = "ai_req_" + uuid.uuid4().hex[:8]
        yield f"event: start\ndata: {json.dumps({'request_id': request_id})}\n\n"

        # 构造 prompt
        prompt = f"面试题目（{q.type}）：\n{q.content}"
        if q.answer:
            prompt += f"\n\n参考信息：\n{q.answer[:500]}"

        client, model = _get_ai_client()
        full_answer = ""
        total_tokens = 0

        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
                temperature=0.7,
                max_tokens=2000,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    yield f"event: chunk\ndata: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
                if chunk.usage:
                    total_tokens = chunk.usage.total_tokens

            yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'total_tokens': total_tokens})}\n\n"

            # 缓存答案
            if full_answer:
                db.add(AiAnswerCache(id=_cache_id(), question_id=question_id, content=full_answer))
                await db.commit()

        except Exception as e:
            error_msg = str(e)
            yield f"event: error\ndata: {json.dumps({'code': 50002, 'message': f'AI 服务异常: {error_msg}'}, ensure_ascii=False)}\n\n"

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
