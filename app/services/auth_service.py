from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.user import User
from app.schemas.auth import (
    WechatLoginRequest, SmsSendRequest, SmsVerifyRequest,
    EmailRegisterRequest, EmailLoginRequest, EmailSendCodeRequest,
    RefreshTokenRequest,
)
from app.cache import (
    set_sms_code, verify_sms_code,
    set_email_code, verify_email_code,
    blacklist_token,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DAILY_FREE_LIMIT = 3
TRIAL_DAYS = 7
EXP_TO_LEVEL = {1: 0, 2: 100, 3: 500, 4: 2000, 5: 5000}
LEVEL_TITLES = {1: "实习生", 2: "初级工程师", 3: "高级工程师", 4: "Offer收割机", 5: "面试之神"}
LEVEL_ICONS = {1: "🌱", 2: "💻", 3: "⭐", 4: "🔥", 5: "👑"}


def _generate_user_id() -> str:
    return "usr_" + uuid.uuid4().hex[:12]


def _jti() -> str:
    """每个 token 的唯一标识，用于黑名单"""
    return uuid.uuid4().hex


def _create_access_token(user_id: str) -> tuple[str, str]:
    """返回 (token, jti)"""
    jti = _jti()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": user_id, "exp": expire, "jti": jti},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return token, jti


def _create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "refresh"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def _build_token_response(user: User, is_new: bool = False) -> dict:
    access_token, _ = _create_access_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": _create_refresh_token(user.id),
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "is_new_user": is_new,
        "user": {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "level": user.level,
            "level_title": LEVEL_TITLES.get(user.level, "实习生"),
            "is_member": user.is_member,
            "member_expires_at": user.member_expires_at.isoformat() if user.member_expires_at else None,
        },
    }


def _new_trial_user(nickname: str) -> User:
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=TRIAL_DAYS)
    return User(
        id=_generate_user_id(),
        nickname=nickname,
        avatar="https://cdn.offerpilot.cn/avatars/default.png",
        is_member=True,
        is_trial=True,
        trial_ends_at=trial_end,
        member_expires_at=trial_end,
        member_plan="trial",
    )


class AuthService:

    @staticmethod
    async def wechat_login(db: AsyncSession, body: WechatLoginRequest) -> dict:
        """
        微信授权码换 openid。
        TODO: 替换 mock，调用真实微信 API:
          GET https://api.weixin.qq.com/sns/jscode2session
              ?appid=&secret=&js_code=&grant_type=authorization_code
        """
        # Mock: 直接用 code 派生 openid，便于本地测试
        openid = f"wx_{body.code[:16]}"

        result = await db.execute(select(User).where(User.wechat_openid == openid))
        user = result.scalar_one_or_none()
        is_new = False
        if not user:
            user = _new_trial_user(f"微信用户{uuid.uuid4().hex[:4].upper()}")
            user.wechat_openid = openid
            db.add(user)
            await db.flush()
            is_new = True
        return _build_token_response(user, is_new)

    @staticmethod
    async def sms_send(db: AsyncSession, body: SmsSendRequest) -> dict:
        """
        生成6位验证码写入 Redis，TTL 300s。
        TODO: 替换 mock，调用阿里云 SMS API 真实发短信。
        """
        code = await set_sms_code(body.phone)
        # 开发环境：将验证码打印到日志，便于测试
        print(f"[DEV] SMS code for {body.phone}: {code}")
        return {"expire_seconds": 300}

    @staticmethod
    async def sms_verify(db: AsyncSession, body: SmsVerifyRequest) -> dict:
        """校验 Redis 中的短信验证码（正确后删除）"""
        ok = await verify_sms_code(body.phone, body.code)
        if not ok:
            raise HTTPException(
                status_code=400,
                detail={"code": 40002, "message": "验证码错误或已过期"},
            )
        result = await db.execute(select(User).where(User.phone == body.phone))
        user = result.scalar_one_or_none()
        is_new = False
        if not user:
            user = _new_trial_user(f"用户{body.phone[-4:]}")
            user.phone = body.phone
            db.add(user)
            await db.flush()
            is_new = True
        return _build_token_response(user, is_new)

    @staticmethod
    async def email_register(db: AsyncSession, body: EmailRegisterRequest) -> dict:
        """邮箱注册：先校验验证码，再创建账号"""
        ok = await verify_email_code(str(body.email), body.verification_code)
        if not ok:
            raise HTTPException(
                status_code=400,
                detail={"code": 40002, "message": "邮箱验证码错误或已过期"},
            )
        result = await db.execute(select(User).where(User.email == str(body.email)))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail={"code": 40005, "message": "该邮箱已注册"},
            )
        user = _new_trial_user(str(body.email).split("@")[0])
        user.email = str(body.email)
        user.password_hash = pwd_context.hash(body.password)
        db.add(user)
        await db.flush()
        return _build_token_response(user, is_new=True)

    @staticmethod
    async def email_login(db: AsyncSession, body: EmailLoginRequest) -> dict:
        result = await db.execute(select(User).where(User.email == str(body.email)))
        user = result.scalar_one_or_none()
        if not user or not user.password_hash or not pwd_context.verify(body.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail={"code": 40001, "message": "邮箱或密码错误"},
            )
        return _build_token_response(user)

    @staticmethod
    async def email_send_code(db: AsyncSession, body: EmailSendCodeRequest) -> dict:
        """
        生成验证码写入 Redis，TTL 300s。
        TODO: 替换 mock，接入 SMTP / SendGrid / 阿里云邮件推送 真实发送。
        """
        code = await set_email_code(str(body.email))
        print(f"[DEV] Email code for {body.email}: {code}")
        return {"expire_seconds": 300}

    @staticmethod
    async def token_refresh(db: AsyncSession, body: RefreshTokenRequest) -> dict:
        try:
            payload = jwt.decode(
                body.refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail={"code": 40001, "message": "Refresh Token 无效或已过期"},
            )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail={"code": 40001, "message": "Token 类型错误"},
            )
        user_id: Optional[str] = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=401,
                detail={"code": 40001, "message": "用户不存在"},
            )
        access_token, _ = _create_access_token(user.id)
        return {
            "access_token": access_token,
            "refresh_token": _create_refresh_token(user.id),
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    async def logout(db: AsyncSession, user_id: str, token: Optional[str] = None) -> None:
        """将当前 access token 的 jti 写入 Redis 黑名单"""
        if token:
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                jti = payload.get("jti")
                if jti:
                    exp = payload.get("exp", 0)
                    ttl = max(0, int(exp - datetime.now(timezone.utc).timestamp()))
                    await blacklist_token(jti, ttl or 1)
            except JWTError:
                pass  # token 已过期，无需处理
