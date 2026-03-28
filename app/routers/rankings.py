from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.schemas.common import Response
from app.services.question_service import QuestionService
from app.models.user import User
from app.models.question import Question
from app.models.social import OriginalConfirm
from app.services.auth_service import LEVEL_TITLES, LEVEL_ICONS

router = APIRouter(prefix="/rankings", tags=["排行榜"])


@router.get("/questions", summary="热门题目排行")
async def get_question_rankings(
    period: str = Query("month", pattern="^(week|month|all)$"),
    company_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await QuestionService.get_hot_questions(
        db, company_id, None, None, period, 1, limit, None
    )
    return Response.ok(result)


@router.get("/users", summary="用户等级排行")
async def get_user_rankings(
    sort_by: str = Query("exp", pattern="^(exp|confirms|questions)$"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    if sort_by == "questions":
        # 按上传题目数排行
        stmt = (
            select(User, func.count(Question.id).label("question_count"))
            .outerjoin(Question, Question.uploader_id == User.id)
            .group_by(User.id)
            .order_by(func.count(Question.id).desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()
        items = [
            {
                "rank": idx + 1,
                "id": user.id,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "level": user.level,
                "level_title": LEVEL_TITLES.get(user.level, "实习生"),
                "level_icon": LEVEL_ICONS.get(user.level, "🌱"),
                "value": count,
                "label": "上传题目数",
            }
            for idx, (user, count) in enumerate(rows)
        ]
    elif sort_by == "confirms":
        # 按收到确认数排行
        stmt = (
            select(User, func.count(OriginalConfirm.id).label("confirm_count"))
            .outerjoin(Question, Question.uploader_id == User.id)
            .outerjoin(OriginalConfirm, OriginalConfirm.question_id == Question.id)
            .group_by(User.id)
            .order_by(func.count(OriginalConfirm.id).desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()
        items = [
            {
                "rank": idx + 1,
                "id": user.id,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "level": user.level,
                "level_title": LEVEL_TITLES.get(user.level, "实习生"),
                "level_icon": LEVEL_ICONS.get(user.level, "🌱"),
                "value": count,
                "label": "收到确认数",
            }
            for idx, (user, count) in enumerate(rows)
        ]
    else:
        # 默认按经验值排行
        stmt = select(User).order_by(User.exp.desc()).limit(limit)
        result = await db.execute(stmt)
        users = result.scalars().all()
        items = [
            {
                "rank": idx + 1,
                "id": u.id,
                "nickname": u.nickname,
                "avatar": u.avatar,
                "level": u.level,
                "level_title": LEVEL_TITLES.get(u.level, "实习生"),
                "level_icon": LEVEL_ICONS.get(u.level, "🌱"),
                "value": u.exp,
                "label": "经验值",
            }
            for idx, u in enumerate(users)
        ]

    return Response.ok({"items": items, "total": len(items)})
