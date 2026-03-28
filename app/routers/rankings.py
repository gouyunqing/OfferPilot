from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.services.question_service import QuestionService

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


@router.get("/users", summary="用户等级排行（V2 预留）")
async def get_user_rankings(
    sort_by: str = Query("exp", pattern="^(exp|confirms|questions)$"),
    limit: int = Query(20, ge=1, le=50),
):
    return Response.ok({
        "items": [],
        "message": "用户排行榜即将上线，敬请期待"
    })
