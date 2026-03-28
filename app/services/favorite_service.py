import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from app.models.social import Favorite
from app.models.question import Question, QuestionCompany
from app.models.user import User

FREE_FAVORITE_LIMIT = 20


def _fav_id() -> str:
    return "fav_" + uuid.uuid4().hex[:9]


class FavoriteService:
    @staticmethod
    async def add_favorite(db: AsyncSession, user_id: str, question_id: str) -> dict:
        existing = (await db.execute(
            select(Favorite).where(Favorite.user_id == user_id, Favorite.question_id == question_id)
        )).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail={"code": 40005, "message": "已收藏"})

        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if user and not user.is_member:
            count = (await db.execute(
                select(func.count()).where(Favorite.user_id == user_id)
            )).scalar() or 0
            if count >= FREE_FAVORITE_LIMIT:
                raise HTTPException(status_code=403, detail={"code": 40003, "message": "免费用户最多收藏 20 题，请开通会员"})

        fav = Favorite(id=_fav_id(), user_id=user_id, question_id=question_id)
        db.add(fav)

        q = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
        if q:
            q.favorite_count += 1

        user_fav_count = (await db.execute(
            select(func.count()).where(Favorite.user_id == user_id)
        )).scalar() or 0

        await db.flush()
        return {
            "favorite_count": user_fav_count + 1,
            "question_favorite_count": q.favorite_count if q else 0,
        }

    @staticmethod
    async def remove_favorite(db: AsyncSession, user_id: str, question_id: str) -> None:
        fav = (await db.execute(
            select(Favorite).where(Favorite.user_id == user_id, Favorite.question_id == question_id)
        )).scalar_one_or_none()
        if not fav:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "未找到收藏记录"})
        q = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
        if q:
            q.favorite_count = max(0, q.favorite_count - 1)
        await db.delete(fav)

    @staticmethod
    async def get_favorites(
        db: AsyncSession,
        user_id: str,
        type: Optional[str],
        company_id: Optional[str],
        page: int,
        page_size: int,
    ) -> dict:
        stmt = select(Question).join(Favorite, Question.id == Favorite.question_id)\
                               .where(Favorite.user_id == user_id)
        if type:
            stmt = stmt.where(Question.type == type)
        if company_id:
            stmt = stmt.join(QuestionCompany, Question.id == QuestionCompany.question_id)\
                       .where(QuestionCompany.company_id == company_id)

        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(stmt.order_by(Favorite.created_at.desc()).offset(offset).limit(page_size))
        questions = result.scalars().all()

        return {
            "items": [{"id": q.id, "content_preview": q.content[:100], "type": q.type} for q in questions],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + len(questions) < total,
        }
