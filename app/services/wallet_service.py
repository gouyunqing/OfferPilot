import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from app.models.wallet import WalletTransaction, Withdrawal
from app.models.user import User
from app.schemas.wallet import WithdrawRequest


def _wd_id() -> str:
    return "wd_" + uuid.uuid4().hex[:9]


class WalletService:
    @staticmethod
    async def get_wallet(db: AsyncSession, user_id: str) -> dict:
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "用户不存在"})

        pending = (await db.execute(
            select(func.sum(Withdrawal.amount))
            .where(Withdrawal.user_id == user_id, Withdrawal.status == "pending")
        )).scalar() or 0.0

        return {
            "balance": user.balance,
            "total_earned": user.total_earned,
            "total_withdrawn": user.total_withdrawn,
            "pending_withdrawal": pending,
        }

    @staticmethod
    async def get_transactions(
        db: AsyncSession, user_id: str, tx_type: Optional[str], page: int, page_size: int
    ) -> dict:
        stmt = select(WalletTransaction).where(WalletTransaction.user_id == user_id)
        if tx_type and tx_type != "all":
            stmt = stmt.where(WalletTransaction.type == tx_type)
        stmt = stmt.order_by(WalletTransaction.created_at.desc())

        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(stmt.offset(offset).limit(page_size))
        txs = result.scalars().all()

        return {
            "items": [
                {
                    "id": t.id,
                    "type": t.type,
                    "amount": t.amount,
                    "description": t.description,
                    "question_id": t.question_id,
                    "status": t.status,
                    "created_at": t.created_at,
                }
                for t in txs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + len(txs) < total,
        }

    @staticmethod
    async def withdraw(db: AsyncSession, user_id: str, body: WithdrawRequest) -> dict:
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "用户不存在"})
        if user.balance < body.amount:
            raise HTTPException(status_code=400, detail={"code": 40007, "message": "余额不足"})

        user.balance -= body.amount
        user.total_withdrawn += body.amount

        wd = Withdrawal(
            id=_wd_id(),
            user_id=user_id,
            amount=body.amount,
            channel=body.channel,
            account=body.account,
            status="pending",
        )
        db.add(wd)

        estimated = datetime.now(timezone.utc) + timedelta(days=1)
        await db.flush()
        return {
            "withdrawal_id": wd.id,
            "amount": wd.amount,
            "channel": wd.channel,
            "status": "pending",
            "estimated_completion": estimated,
            "message": "提现申请已提交，预计 T+1 工作日到账",
        }

    @staticmethod
    async def get_withdrawals(db: AsyncSession, user_id: str, page: int, page_size: int) -> dict:
        stmt = select(Withdrawal).where(Withdrawal.user_id == user_id).order_by(Withdrawal.created_at.desc())
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(stmt.offset(offset).limit(page_size))
        wds = result.scalars().all()
        return {
            "items": [
                {
                    "id": w.id,
                    "amount": w.amount,
                    "channel": w.channel,
                    "status": w.status,
                    "created_at": w.created_at,
                }
                for w in wds
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + len(wds) < total,
        }
