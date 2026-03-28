from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.schemas.subscription import AppleVerifyRequest
from app.services.subscription_service import SubscriptionService
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/subscriptions", tags=["订阅"])


@router.get("/plans", summary="获取订阅方案列表")
async def get_plans():
    result = await SubscriptionService.get_plans()
    return Response.ok(result)


@router.post("/apple/verify", summary="验证 Apple IAP 收据")
async def apple_verify(
    body: AppleVerifyRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await SubscriptionService.apple_verify(db, user_id, body)
    return Response.ok(result)


@router.get("/me", summary="获取当前订阅状态")
async def get_subscription_status(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await SubscriptionService.get_status(db, user_id)
    return Response.ok(result)


@router.post("/apple/webhook", summary="Apple 服务端通知回调")
async def apple_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.json()
    await SubscriptionService.handle_apple_webhook(db, payload)
    return {"status": "ok"}
