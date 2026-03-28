import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.social import OriginalConfirm
from app.models.question import Question
from app.models.user import User
from app.models.wallet import WalletTransaction

MAX_REWARD = 5.0
REWARD_PER_CONFIRM = 0.5


def _confirm_id() -> str:
    return "conf_" + uuid.uuid4().hex[:9]


def _tx_id() -> str:
    return "tx_" + uuid.uuid4().hex[:9]


class ConfirmService:
    @staticmethod
    async def confirm(db: AsyncSession, question_id: str, user_id: str) -> dict:
        # Check duplicate
        existing = (await db.execute(
            select(OriginalConfirm).where(
                OriginalConfirm.question_id == question_id,
                OriginalConfirm.user_id == user_id,
            )
        )).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail={"code": 40005, "message": "你已经确认过这道题了"})

        q = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
        if not q:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "题目不存在"})

        confirm = OriginalConfirm(id=_confirm_id(), question_id=question_id, user_id=user_id)
        db.add(confirm)
        q.confirm_count += 1

        reward_sent = False
        reward_amount = 0.0
        if q.reward_total < MAX_REWARD:
            reward_amount = min(REWARD_PER_CONFIRM, MAX_REWARD - q.reward_total)
            q.reward_total += reward_amount

            # Credit uploader
            uploader = (await db.execute(select(User).where(User.id == q.uploader_id))).scalar_one_or_none()
            if uploader:
                uploader.balance += reward_amount
                uploader.total_earned += reward_amount
                uploader.exp += 20
                db.add(WalletTransaction(
                    id=_tx_id(),
                    user_id=uploader.id,
                    type="reward",
                    amount=reward_amount,
                    description=f"题目「{q.content[:20]}」被确认为原题",
                    question_id=question_id,
                    status="completed",
                ))
            reward_sent = True

        await db.flush()
        return {
            "confirm_count": q.confirm_count,
            "reward_sent": reward_sent,
            "reward_amount": reward_amount,
            "uploader_total_reward": q.reward_total,
            "message": f"确认成功！题目上传者获得 ¥{reward_amount:.2f} 奖励" if reward_sent else "确认成功！奖励已达上限",
        }

    @staticmethod
    async def unconfirm(db: AsyncSession, question_id: str, user_id: str) -> dict:
        existing = (await db.execute(
            select(OriginalConfirm).where(
                OriginalConfirm.question_id == question_id,
                OriginalConfirm.user_id == user_id,
            )
        )).scalar_one_or_none()
        if not existing:
            raise HTTPException(status_code=400, detail={"code": 40004, "message": "未找到确认记录"})

        q = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
        if q:
            q.confirm_count = max(0, q.confirm_count - 1)
        await db.delete(existing)
        return {"confirm_count": q.confirm_count if q else 0}
