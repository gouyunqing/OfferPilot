from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.schemas.user import UserUpdateRequest
from app.services.user_service import UserService
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", summary="获取当前用户信息")
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await UserService.get_me(db, user_id)
    return Response.ok(result)


@router.patch("/me", summary="更新用户信息")
async def update_me(
    body: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await UserService.update_me(db, user_id, body)
    return Response.ok(result)


@router.get("/me/questions", summary="获取我上传的题目列表")
async def get_my_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await UserService.get_my_questions(db, user_id, page, page_size)
    return Response.ok(result)


@router.get("/{user_id}/profile", summary="获取用户公开主页")
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await UserService.get_user_profile(db, user_id)
    return Response.ok(result)
