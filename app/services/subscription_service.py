import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription import AppleVerifyRequest

PLANS = [
    {
        "id": "plan_continuous_monthly",
        "name": "连续包月",
        "price": 25.00,
        "period_months": 1,
        "auto_renew": True,
        "apple_product_id": "com.offerpilot.sub.continuous_monthly",
        "discount_label": "最优惠",
        "original_price": 30.00,
    },
    {
        "id": "plan_monthly",
        "name": "月订阅",
        "price": 30.00,
        "period_months": 1,
        "auto_renew": False,
        "apple_product_id": "com.offerpilot.sub.monthly",
        "discount_label": None,
        "original_price": 30.00,
    },
    {
        "id": "plan_quarterly",
        "name": "季订阅",
        "price": 68.00,
        "period_months": 3,
        "auto_renew": False,
        "apple_product_id": "com.offerpilot.sub.quarterly",
        "discount_label": "约7.6折",
        "original_price": 90.00,
    },
    {
        "id": "plan_yearly",
        "name": "年订阅",
        "price": 228.00,
        "period_months": 12,
        "auto_renew": False,
        "apple_product_id": "com.offerpilot.sub.yearly",
        "discount_label": "约6.3折",
        "original_price": 360.00,
    },
]

PLAN_MAP = {p["apple_product_id"]: p for p in PLANS}


def _sub_id() -> str:
    return "sub_" + uuid.uuid4().hex[:9]


class SubscriptionService:
    @staticmethod
    async def get_plans() -> dict:
        return {"plans": PLANS}

    @staticmethod
    async def apple_verify(db: AsyncSession, user_id: str, body: AppleVerifyRequest) -> dict:
        # TODO: verify receipt with Apple App Store API
        plan = PLAN_MAP.get(body.product_id, PLANS[1])
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=30 * plan["period_months"])

        sub = Subscription(
            id=_sub_id(),
            user_id=user_id,
            plan_type=plan["id"],
            apple_transaction_id=body.transaction_id,
            apple_product_id=body.product_id,
            status="active",
            auto_renew=plan["auto_renew"],
            starts_at=now,
            expires_at=expires,
        )
        db.add(sub)

        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if user:
            user.is_member = True
            user.is_trial = False
            user.member_plan = plan["name"]
            user.member_expires_at = expires

        await db.flush()
        return {
            "subscription": {
                "id": sub.id,
                "plan": plan["name"],
                "status": "active",
                "starts_at": sub.starts_at,
                "expires_at": sub.expires_at,
                "auto_renew": sub.auto_renew,
            },
            "message": "订阅开通成功！",
        }

    @staticmethod
    async def get_status(db: AsyncSession, user_id: str) -> dict:
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail={"code": 40004, "message": "用户不存在"})

        sub = (await db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id, Subscription.status == "active")
            .order_by(Subscription.expires_at.desc())
        )).scalar_one_or_none()

        return {
            "is_member": user.is_member,
            "is_trial": user.is_trial,
            "plan": user.member_plan,
            "status": "active" if user.is_member else "inactive",
            "starts_at": sub.starts_at if sub else None,
            "expires_at": user.member_expires_at,
            "auto_renew": sub.auto_renew if sub else False,
            "trial_ends_at": user.trial_ends_at,
        }

    @staticmethod
    async def handle_apple_webhook(db: AsyncSession, payload: dict) -> None:
        # TODO: validate Apple notification signature and update subscription status
        pass
