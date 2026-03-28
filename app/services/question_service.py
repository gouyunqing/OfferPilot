import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from fastapi import HTTPException

from app.models.question import Question, QuestionCompany
from app.models.meta import Company, Position
from app.models.user import User
from app.models.social import Favorite, OriginalConfirm
from app.schemas.question import QuestionCreateRequest, QuestionType, RecruitType, RoundType, SortBy
from app.services.auth_service import LEVEL_TITLES, LEVEL_ICONS
from app.services.user_service import reset_daily_free_if_needed

DAILY_FREE_LIMIT = 3
MAX_REWARD_PER_QUESTION = 5.0
REWARD_PER_CONFIRM = 0.5


def _question_id() -> str:
    return "q_" + uuid.uuid4().hex[:9]


async def _build_question_items(
    db: AsyncSession, questions: List[Question], current_user_id: Optional[str]
) -> list:
    """批量构建题目列表项，避免 N+1 查询"""
    if not questions:
        return []

    q_ids = [q.id for q in questions]
    uploader_ids = list({q.uploader_id for q in questions})
    position_ids = list({q.position_id for q in questions if q.position_id})

    # 批量查询公司关联
    qc_result = await db.execute(
        select(QuestionCompany.question_id, Company)
        .join(Company, Company.id == QuestionCompany.company_id)
        .where(QuestionCompany.question_id.in_(q_ids))
    )
    companies_map = {}
    for qid, company in qc_result.all():
        companies_map.setdefault(qid, []).append(company)

    # 批量查询岗位
    positions_map = {}
    if position_ids:
        pos_result = await db.execute(select(Position).where(Position.id.in_(position_ids)))
        for p in pos_result.scalars().all():
            positions_map[p.id] = p

    # 批量查询上传者
    up_result = await db.execute(select(User).where(User.id.in_(uploader_ids)))
    uploaders_map = {u.id: u for u in up_result.scalars().all()}

    # 批量查询当前用户的收藏和确认状态
    favorited_set = set()
    confirmed_set = set()
    if current_user_id:
        fav_result = await db.execute(
            select(Favorite.question_id)
            .where(Favorite.user_id == current_user_id, Favorite.question_id.in_(q_ids))
        )
        favorited_set = {row[0] for row in fav_result.all()}

        conf_result = await db.execute(
            select(OriginalConfirm.question_id)
            .where(OriginalConfirm.user_id == current_user_id, OriginalConfirm.question_id.in_(q_ids))
        )
        confirmed_set = {row[0] for row in conf_result.all()}

    items = []
    for q in questions:
        companies = companies_map.get(q.id, [])
        position = positions_map.get(q.position_id)
        uploader = uploaders_map.get(q.uploader_id)

        interview_time = None
        if q.interview_year:
            interview_time = f"{q.interview_year}-Q{q.interview_quarter}" if q.interview_quarter else str(q.interview_year)

        items.append({
            "id": q.id,
            "type": q.type,
            "content_preview": q.content[:100] + ("..." if len(q.content) > 100 else ""),
            "has_answer": bool(q.answer),
            "companies": [{"id": c.id, "name": c.name, "logo": c.logo} for c in companies],
            "position": {"id": position.id, "name": position.name} if position else None,
            "recruit_type": q.recruit_type,
            "round": q.round,
            "interview_time": interview_time,
            "confirm_count": q.confirm_count,
            "comment_count": q.comment_count,
            "favorite_count": q.favorite_count,
            "is_favorited": q.id in favorited_set if current_user_id else None,
            "is_confirmed": q.id in confirmed_set if current_user_id else None,
            "uploader": {
                "id": uploader.id,
                "nickname": uploader.nickname,
                "level": uploader.level,
                "level_icon": LEVEL_ICONS.get(uploader.level, "🌱"),
            } if uploader else None,
            "created_at": q.created_at,
        })

    return items


async def _build_single_question_item(
    db: AsyncSession, q: Question, current_user_id: Optional[str]
) -> dict:
    """单个题目详情（复用批量函数）"""
    items = await _build_question_items(db, [q], current_user_id)
    return items[0]


class QuestionService:
    @staticmethod
    async def get_questions(
        db: AsyncSession,
        type: Optional[QuestionType],
        company_id: Optional[str],
        position_id: Optional[str],
        recruit_type: Optional[RecruitType],
        round: Optional[RoundType],
        sort_by: SortBy,
        keyword: Optional[str],
        year: Optional[int],
        quarter: Optional[int],
        page: int,
        page_size: int,
        current_user_id: Optional[str],
    ) -> dict:
        stmt = select(Question).where(Question.status == "approved")
        if type:
            stmt = stmt.where(Question.type == type)
        if position_id:
            stmt = stmt.where(Question.position_id == position_id)
        if recruit_type:
            stmt = stmt.where(Question.recruit_type == recruit_type)
        if round:
            stmt = stmt.where(Question.round == round)
        if keyword:
            stmt = stmt.where(or_(
                Question.content.ilike(f"%{keyword}%"),
                Question.answer.ilike(f"%{keyword}%"),
            ))
        if year:
            stmt = stmt.where(Question.interview_year == year)
        if quarter:
            stmt = stmt.where(Question.interview_quarter == quarter)
        if company_id:
            stmt = stmt.join(QuestionCompany, Question.id == QuestionCompany.question_id)\
                       .where(QuestionCompany.company_id == company_id)

        if sort_by == SortBy.hot:
            stmt = stmt.order_by((Question.confirm_count * 3 + Question.favorite_count).desc())
        elif sort_by == SortBy.most_confirmed:
            stmt = stmt.order_by(Question.confirm_count.desc())
        else:
            stmt = stmt.order_by(Question.created_at.desc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        offset = (page - 1) * page_size
        result = await db.execute(stmt.offset(offset).limit(page_size))
        questions = result.scalars().all()

        items = await _build_question_items(db, questions, current_user_id)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + len(items) < total,
        }

    @staticmethod
    async def get_question_detail(db: AsyncSession, question_id: str, user_id: str) -> dict:
        result = await db.execute(select(Question).where(Question.id == question_id))
        q = result.scalar_one_or_none()
        if not q:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "题目不存在"})

        # Check user quota
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user and not user.is_member:
            reset_daily_free_if_needed(user)
            if (user.daily_free_used or 0) >= DAILY_FREE_LIMIT:
                raise HTTPException(status_code=403, detail={"code": 40006, "message": "免费额度已用完，请开通会员"})
            user.daily_free_used = (user.daily_free_used or 0) + 1

        item = await _build_single_question_item(db, q, user_id)
        item["content"] = q.content
        item["answer"] = q.answer
        item["reward_remaining"] = max(0, MAX_REWARD_PER_QUESTION - q.reward_total)
        del item["content_preview"]
        return item

    @staticmethod
    async def create_question(db: AsyncSession, user_id: str, body: QuestionCreateRequest) -> dict:
        q = Question(
            id=_question_id(),
            type=body.type,
            content=body.content,
            answer=body.answer,
            uploader_id=user_id,
            position_id=body.position_id,
            recruit_type=body.recruit_type,
            round=body.round,
            interview_year=body.interview_year,
            interview_quarter=body.interview_quarter,
            leetcode_number=body.leetcode_number,
            leetcode_url=body.leetcode_url,
            status="approved",
        )
        db.add(q)
        await db.flush()
        for company_id in body.company_ids:
            db.add(QuestionCompany(question_id=q.id, company_id=company_id))

        # Award exp
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.exp += 10

        return {
            "id": q.id,
            "type": q.type,
            "status": q.status,
            "exp_gained": 10,
            "message": "题目发布成功！获得 10 经验值",
        }

    @staticmethod
    async def get_hot_questions(
        db: AsyncSession,
        company_id: Optional[str],
        position_id: Optional[str],
        recruit_type: Optional[RecruitType],
        period: str,
        page: int,
        page_size: int,
        current_user_id: Optional[str],
    ) -> dict:
        from datetime import datetime, timedelta, timezone
        stmt = select(Question).where(Question.status == "approved")
        if period == "week":
            cutoff = datetime.now(timezone.utc) - timedelta(weeks=1)
            stmt = stmt.where(Question.created_at >= cutoff)
        elif period == "month":
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            stmt = stmt.where(Question.created_at >= cutoff)
        if company_id:
            stmt = stmt.join(QuestionCompany, Question.id == QuestionCompany.question_id)\
                       .where(QuestionCompany.company_id == company_id)
        if position_id:
            stmt = stmt.where(Question.position_id == position_id)
        if recruit_type:
            stmt = stmt.where(Question.recruit_type == recruit_type)
        stmt = stmt.order_by((Question.confirm_count * 3 + Question.favorite_count).desc())

        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(stmt.offset(offset).limit(page_size))
        questions = result.scalars().all()
        items = await _build_question_items(db, questions, current_user_id)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + len(items) < total,
        }

    @staticmethod
    async def search_questions(
        db: AsyncSession,
        q: str,
        type: Optional[QuestionType],
        company_id: Optional[str],
        page: int,
        page_size: int,
        current_user_id: Optional[str],
    ) -> dict:
        return await QuestionService.get_questions(
            db, type, company_id, None, None, None,
            SortBy.latest, q, None, None, page, page_size, current_user_id
        )
