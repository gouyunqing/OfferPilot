from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.schemas.auth import (
    WechatLoginRequest, SmsSendRequest, SmsVerifyRequest,
    EmailRegisterRequest, EmailLoginRequest, EmailSendCodeRequest,
    RefreshTokenRequest, TokenResponse, SmsExpireResponse,
)
from app.services.auth_service import AuthService
from app.dependencies import get_current_user_id, get_raw_token

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/wechat", summary="微信登录")
async def wechat_login(body: WechatLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await AuthService.wechat_login(db, body)
    return Response.ok(result)


@router.post("/sms/send", summary="发送短信验证码")
async def sms_send(body: SmsSendRequest, db: AsyncSession = Depends(get_db)):
    result = await AuthService.sms_send(db, body)
    return Response.ok(result)


@router.post("/sms/verify", summary="手机号验证码登录")
async def sms_verify(body: SmsVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await AuthService.sms_verify(db, body)
    return Response.ok(result)


@router.post("/email/register", summary="邮箱注册")
async def email_register(body: EmailRegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await AuthService.email_register(db, body)
    return Response.ok(result)


@router.post("/email/login", summary="邮箱登录")
async def email_login(body: EmailLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await AuthService.email_login(db, body)
    return Response.ok(result)


@router.post("/email/send-code", summary="发送邮箱验证码")
async def email_send_code(body: EmailSendCodeRequest, db: AsyncSession = Depends(get_db)):
    result = await AuthService.email_send_code(db, body)
    return Response.ok(result)


@router.post("/token/refresh", summary="刷新 Token")
async def token_refresh(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    result = await AuthService.token_refresh(db, body)
    return Response.ok(result)


@router.post("/logout", summary="退出登录")
async def logout(
    user_id: str = Depends(get_current_user_id),
    token: str = Depends(get_raw_token),
    db: AsyncSession = Depends(get_db),
):
    await AuthService.logout(db, user_id, token)
    return Response.ok()
