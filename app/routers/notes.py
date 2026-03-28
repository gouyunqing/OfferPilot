from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.services.note_service import NoteService
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/notes", tags=["笔记"])


@router.get("", summary="获取所有笔记列表")
async def get_all_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await NoteService.get_all_notes(db, user_id, page, page_size)
    return Response.ok(result)
