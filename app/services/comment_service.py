import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.comment import Comment, CommentVote
from app.models.user import User
from app.models.question import Question
from app.schemas.comment import CommentCreateRequest, CommentVoteRequest, VoteType
from app.services.auth_service import LEVEL_ICONS


def _comment_id() -> str:
    return "cmt_" + uuid.uuid4().hex[:9]


def _vote_id() -> str:
    return "vote_" + uuid.uuid4().hex[:9]


class CommentService:
    @staticmethod
    async def get_comments(
        db: AsyncSession,
        question_id: str,
        sort_by: str,
        page: int,
        page_size: int,
        current_user_id: Optional[str],
    ) -> dict:
        from sqlalchemy import func
        stmt = select(Comment).where(Comment.question_id == question_id)
        if sort_by == "latest":
            stmt = stmt.order_by(Comment.created_at.desc())
        else:
            stmt = stmt.order_by(Comment.upvotes.desc())

        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(stmt.offset(offset).limit(page_size))
        comments = result.scalars().all()

        # Determine if current user is member (for blur)
        is_member = False
        if current_user_id:
            u = (await db.execute(select(User).where(User.id == current_user_id))).scalar_one_or_none()
            is_member = bool(u and u.is_member)

        items = []
        for c in comments:
            u = (await db.execute(select(User).where(User.id == c.user_id))).scalar_one_or_none()
            blurred = not is_member
            my_vote = None
            if current_user_id:
                v = (await db.execute(
                    select(CommentVote).where(
                        CommentVote.comment_id == c.id,
                        CommentVote.user_id == current_user_id,
                    )
                )).scalar_one_or_none()
                my_vote = v.vote_type if v else None
            items.append({
                "id": c.id,
                "content": c.content[:20] + "..." if blurred else c.content,
                "content_blurred": blurred,
                "user": {
                    "id": u.id if u else "",
                    "nickname": u.nickname if u else "已注销",
                    "level": u.level if u else 1,
                    "level_icon": LEVEL_ICONS.get(u.level, "🌱") if u else "🌱",
                },
                "upvotes": c.upvotes,
                "downvotes": c.downvotes,
                "my_vote": my_vote,
                "created_at": c.created_at,
            })
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + len(items) < total,
        }

    @staticmethod
    async def create_comment(
        db: AsyncSession,
        question_id: str,
        user_id: str,
        body: CommentCreateRequest,
    ) -> dict:
        c = Comment(
            id=_comment_id(),
            question_id=question_id,
            user_id=user_id,
            content=body.content,
        )
        db.add(c)

        # Update question comment count
        q = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
        if q:
            q.comment_count += 1

        # Award exp
        u = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if u:
            u.exp += 5

        await db.flush()
        return {
            "id": c.id,
            "content": c.content,
            "exp_gained": 5,
            "message": "评论发布成功！获得 5 经验值",
        }

    @staticmethod
    async def vote_comment(
        db: AsyncSession,
        comment_id: str,
        user_id: str,
        body: CommentVoteRequest,
    ) -> dict:
        c = (await db.execute(select(Comment).where(Comment.id == comment_id))).scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "评论不存在"})

        existing = (await db.execute(
            select(CommentVote).where(CommentVote.comment_id == comment_id, CommentVote.user_id == user_id)
        )).scalar_one_or_none()

        if body.vote_type == VoteType.cancel:
            if existing:
                if existing.vote_type == "up":
                    c.upvotes = max(0, c.upvotes - 1)
                else:
                    c.downvotes = max(0, c.downvotes - 1)
                await db.delete(existing)
            my_vote = None
        else:
            if existing:
                # Switch vote
                if existing.vote_type != body.vote_type:
                    if existing.vote_type == "up":
                        c.upvotes = max(0, c.upvotes - 1)
                        c.downvotes += 1
                    else:
                        c.downvotes = max(0, c.downvotes - 1)
                        c.upvotes += 1
                    existing.vote_type = body.vote_type
            else:
                vote = CommentVote(
                    id=_vote_id(),
                    comment_id=comment_id,
                    user_id=user_id,
                    vote_type=body.vote_type,
                )
                db.add(vote)
                if body.vote_type == "up":
                    c.upvotes += 1
                else:
                    c.downvotes += 1
            my_vote = body.vote_type

        return {"upvotes": c.upvotes, "downvotes": c.downvotes, "my_vote": my_vote}

    @staticmethod
    async def delete_comment(db: AsyncSession, comment_id: str, user_id: str) -> None:
        c = (await db.execute(select(Comment).where(Comment.id == comment_id))).scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "评论不存在"})
        if c.user_id != user_id:
            raise HTTPException(status_code=403, detail={"code": 40003, "message": "无权删除此评论"})
        await db.delete(c)
