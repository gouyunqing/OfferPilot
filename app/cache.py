"""
Redis 缓存工具：验证码存取、Token 黑名单
"""
from __future__ import annotations
import random
import string
from typing import Optional

from app.redis_client import get_redis

# Key 前缀
_SMS_PREFIX = "sms:code:"
_EMAIL_PREFIX = "email:code:"
_TOKEN_BLACKLIST = "token:blacklist:"

SMS_CODE_TTL = 300       # 5 分钟
EMAIL_CODE_TTL = 300
TOKEN_BLACKLIST_TTL = 7200  # 与 access_token 有效期相同


def _rand_code(n: int = 6) -> str:
    return "".join(random.choices(string.digits, k=n))


# ---------- 短信验证码 ----------

async def set_sms_code(phone: str, code: Optional[str] = None) -> str:
    """生成并缓存短信验证码，返回验证码"""
    code = code or _rand_code()
    r = await get_redis()
    await r.setex(f"{_SMS_PREFIX}{phone}", SMS_CODE_TTL, code)
    return code


async def verify_sms_code(phone: str, code: str) -> bool:
    """校验短信验证码，验证成功后删除"""
    r = await get_redis()
    stored = await r.get(f"{_SMS_PREFIX}{phone}")
    if stored and stored == code:
        await r.delete(f"{_SMS_PREFIX}{phone}")
        return True
    return False


# ---------- 邮箱验证码 ----------

async def set_email_code(email: str, code: Optional[str] = None) -> str:
    code = code or _rand_code()
    r = await get_redis()
    await r.setex(f"{_EMAIL_PREFIX}{email}", EMAIL_CODE_TTL, code)
    return code


async def verify_email_code(email: str, code: str) -> bool:
    r = await get_redis()
    stored = await r.get(f"{_EMAIL_PREFIX}{email}")
    if stored and stored == code:
        await r.delete(f"{_EMAIL_PREFIX}{email}")
        return True
    return False


# ---------- Token 黑名单（logout 时写入） ----------

async def blacklist_token(jti: str, ttl: int = TOKEN_BLACKLIST_TTL) -> None:
    """将 token jti 加入黑名单，ttl 秒后自动过期"""
    r = await get_redis()
    await r.setex(f"{_TOKEN_BLACKLIST}{jti}", ttl, "1")


async def is_token_blacklisted(jti: str) -> bool:
    r = await get_redis()
    return bool(await r.exists(f"{_TOKEN_BLACKLIST}{jti}"))
