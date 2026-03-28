from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re


class WechatLoginRequest(BaseModel):
    code: str
    device_id: str


class SmsSendRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class SmsVerifyRequest(BaseModel):
    phone: str
    code: str
    device_id: str


class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    verification_code: str


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str


class EmailSendCodeRequest(BaseModel):
    email: EmailStr


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    is_new_user: bool = False
    user: Optional[dict] = None


class SmsExpireResponse(BaseModel):
    expire_seconds: int = 300
