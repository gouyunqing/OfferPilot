from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    id: str
    nickname: str
    avatar: str
    level: int
    level_title: str
    is_member: bool


class UserPublicProfile(UserBase):
    level_icon: str
    exp: int
    question_count: int
    confirm_received_count: int
    created_at: datetime


class UserMe(UserBase):
    phone: Optional[str] = None
    email: Optional[str] = None
    level_icon: str
    exp: int
    exp_to_next_level: int
    member_plan: Optional[str] = None
    member_expires_at: Optional[datetime] = None
    balance: float
    question_count: int
    comment_count: int
    confirm_received_count: int
    favorite_count: int
    daily_free_remaining: int
    created_at: datetime


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserUpdateResponse(BaseModel):
    id: str
    nickname: str
    avatar: str
