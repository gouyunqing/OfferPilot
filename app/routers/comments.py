from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.schemas.comment import CommentVoteRequest
from app.services.comment_service import CommentService
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/comments", tags=["评论"])


@router.post("/{comment_id}/vote", summary="评论投票")
async def vote_comment(
    comment_id: str,
    body: CommentVoteRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await CommentService.vote_comment(db, comment_id, user_id, body)
    return Response.ok(result)


@router.delete("/{comment_id}", summary="删除评论")
async def delete_comment(
    comment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await CommentService.delete_comment(db, comment_id, user_id)
    return Response(code=0, message="评论已删除")
