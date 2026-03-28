from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.schemas.favorite import FavoriteCreateRequest
from app.schemas.question import QuestionType
from app.services.favorite_service import FavoriteService
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/favorites", tags=["收藏"])


@router.get("", summary="获取收藏列表")
async def get_favorites(
    type: Optional[QuestionType] = None,
    company_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await FavoriteService.get_favorites(db, user_id, type, company_id, page, page_size)
    return Response.ok(result)


@router.post("", summary="收藏题目")
async def add_favorite(
    body: FavoriteCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await FavoriteService.add_favorite(db, user_id, body.question_id)
    return Response.ok(result)


@router.delete("/{question_id}", summary="取消收藏")
async def remove_favorite(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await FavoriteService.remove_favorite(db, user_id, question_id)
    return Response(code=0, message="已取消收藏")
