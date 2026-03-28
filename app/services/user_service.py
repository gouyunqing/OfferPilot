from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from app.models.user import User
from app.models.question import Question
from app.models.comment import Comment
from app.models.social import OriginalConfirm, Favorite
from app.schemas.user import UserUpdateRequest
from app.services.auth_service import LEVEL_TITLES, LEVEL_ICONS, EXP_TO_LEVEL

DAILY_FREE_LIMIT = 3


def reset_daily_free_if_needed(user: User) -> None:
    """如果上次重置日期不是今天，重置每日免费次数"""
    now = datetime.now(timezone.utc)
    today = now.date()
    last_reset = user.daily_free_reset_at
    if last_reset is None or last_reset.date() < today:
        user.daily_free_used = 0
        user.daily_free_reset_at = now


def _exp_to_next(level: int, exp: int) -> int:
    next_level = level + 1
    if next_level > 5:
        return 0
    return EXP_TO_LEVEL[next_level] - exp


class UserService:
    @staticmethod
    async def get_me(db: AsyncSession, user_id: str) -> dict:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "用户不存在"})

        reset_daily_free_if_needed(user)

        question_count = (await db.execute(
            select(func.count()).where(Question.uploader_id == user_id)
        )).scalar() or 0

        comment_count = (await db.execute(
            select(func.count()).where(Comment.user_id == user_id)
        )).scalar() or 0

        # 收到的确认数 = 我上传的题目被别人确认的次数
        confirm_received_count = (await db.execute(
            select(func.count()).select_from(OriginalConfirm)
            .join(Question, OriginalConfirm.question_id == Question.id)
            .where(Question.uploader_id == user_id)
        )).scalar() or 0

        favorite_count = (await db.execute(
            select(func.count()).where(Favorite.user_id == user_id)
        )).scalar() or 0

        daily_remaining = max(0, DAILY_FREE_LIMIT - (user.daily_free_used or 0))

        return {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "phone": f"{user.phone[:3]}****{user.phone[-4:]}" if user.phone else None,
            "email": f"{user.email[:1]}***@{user.email.split('@')[1]}" if user.email else None,
            "level": user.level,
            "level_title": LEVEL_TITLES.get(user.level, "实习生"),
            "level_icon": LEVEL_ICONS.get(user.level, "🌱"),
            "exp": user.exp,
            "exp_to_next_level": _exp_to_next(user.level, user.exp),
            "is_member": user.is_member,
            "member_plan": user.member_plan,
            "member_expires_at": user.member_expires_at,
            "balance": user.balance,
            "question_count": question_count,
            "comment_count": comment_count,
            "confirm_received_count": confirm_received_count,
            "favorite_count": favorite_count,
            "daily_free_remaining": daily_remaining,
            "created_at": user.created_at,
        }

    @staticmethod
    async def update_me(db: AsyncSession, user_id: str, body: UserUpdateRequest) -> dict:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "用户不存在"})
        if body.nickname is not None:
            user.nickname = body.nickname
        if body.avatar is not None:
            user.avatar = body.avatar
        return {"id": user.id, "nickname": user.nickname, "avatar": user.avatar}

    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: str) -> dict:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "用户不存在"})
        question_count = (await db.execute(
            select(func.count()).where(Question.uploader_id == user_id)
        )).scalar() or 0

        confirm_received_count = (await db.execute(
            select(func.count()).select_from(OriginalConfirm)
            .join(Question, OriginalConfirm.question_id == Question.id)
            .where(Question.uploader_id == user_id)
        )).scalar() or 0

        return {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "level": user.level,
            "level_title": LEVEL_TITLES.get(user.level, "实习生"),
            "level_icon": LEVEL_ICONS.get(user.level, "🌱"),
            "exp": user.exp,
            "question_count": question_count,
            "confirm_received_count": confirm_received_count,
            "created_at": user.created_at,
        }

    @staticmethod
    async def get_my_questions(db: AsyncSession, user_id: str, page: int, page_size: int) -> dict:
        offset = (page - 1) * page_size
        total_result = await db.execute(
            select(func.count()).where(Question.uploader_id == user_id)
        )
        total = total_result.scalar() or 0
        result = await db.execute(
            select(Question)
            .where(Question.uploader_id == user_id)
            .order_by(Question.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        questions = result.scalars().all()
        return {
            "items": [{"id": q.id, "content_preview": q.content[:100], "type": q.type} for q in questions],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + len(questions) < total,
        }
