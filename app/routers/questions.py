from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.schemas.question import QuestionCreateRequest, QuestionType, RecruitType, RoundType, SortBy
from app.schemas.comment import CommentCreateRequest
from app.schemas.note import NoteUpsertRequest
from app.services.question_service import QuestionService
from app.services.comment_service import CommentService
from app.services.confirm_service import ConfirmService
from app.services.note_service import NoteService
from app.dependencies import get_current_user_id, get_optional_user_id

router = APIRouter(prefix="/questions", tags=["题目"])


@router.get("/hot", summary="热门题目排行")
async def get_hot_questions(
    company_id: Optional[str] = None,
    position_id: Optional[str] = None,
    recruit_type: Optional[RecruitType] = None,
    period: str = Query("month", pattern="^(week|month|all)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user_id: Optional[str] = Depends(get_optional_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await QuestionService.get_hot_questions(
        db, company_id, position_id, recruit_type, period, page, page_size, current_user_id
    )
    return Response.ok(result)


@router.get("/search", summary="搜索题目")
async def search_questions(
    q: str = Query(..., min_length=1),
    type: Optional[QuestionType] = None,
    company_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user_id: Optional[str] = Depends(get_optional_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await QuestionService.search_questions(
        db, q, type, company_id, page, page_size, current_user_id
    )
    return Response.ok(result)


@router.get("", summary="获取题目列表")
async def get_questions(
    type: Optional[QuestionType] = None,
    company_id: Optional[str] = None,
    position_id: Optional[str] = None,
    recruit_type: Optional[RecruitType] = None,
    round: Optional[RoundType] = None,
    sort_by: SortBy = SortBy.latest,
    keyword: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user_id: Optional[str] = Depends(get_optional_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await QuestionService.get_questions(
        db, type, company_id, position_id, recruit_type, round,
        sort_by, keyword, year, quarter, page, page_size, current_user_id
    )
    return Response.ok(result)


@router.post("", summary="上传题目")
async def create_question(
    body: QuestionCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await QuestionService.create_question(db, user_id, body)
    return Response.ok(result)


@router.get("/{question_id}", summary="获取题目详情")
async def get_question(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await QuestionService.get_question_detail(db, question_id, user_id)
    return Response.ok(result)


@router.get("/{question_id}/comments", summary="获取题目评论列表")
async def get_question_comments(
    question_id: str,
    sort_by: str = Query("upvotes", pattern="^(upvotes|latest)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user_id: Optional[str] = Depends(get_optional_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.comment_service import CommentService
    result = await CommentService.get_comments(
        db, question_id, sort_by, page, page_size, current_user_id
    )
    return Response.ok(result)


@router.post("/{question_id}/comments", summary="发表评论")
async def create_comment(
    question_id: str,
    body: CommentCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await CommentService.create_comment(db, question_id, user_id, body)
    return Response.ok(result)


@router.post("/{question_id}/confirm", summary="确认原题")
async def confirm_question(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await ConfirmService.confirm(db, question_id, user_id)
    return Response.ok(result)


@router.delete("/{question_id}/confirm", summary="取消确认原题")
async def unconfirm_question(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await ConfirmService.unconfirm(db, question_id, user_id)
    return Response.ok(result)


@router.put("/{question_id}/note", summary="添加/更新笔记")
async def upsert_note(
    question_id: str,
    body: NoteUpsertRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await NoteService.upsert_note(db, question_id, user_id, body)
    return Response.ok(result)


@router.get("/{question_id}/note", summary="获取笔记")
async def get_note(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await NoteService.get_note(db, question_id, user_id)
    return Response.ok(result)


@router.delete("/{question_id}/note", summary="删除笔记")
async def delete_note(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await NoteService.delete_note(db, question_id, user_id)
    return Response(code=0, message="笔记已删除")
