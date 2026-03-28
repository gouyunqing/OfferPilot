from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum


class WithdrawChannel(str, Enum):
    wechat = "wechat"
    alipay = "alipay"


class WalletInfo(BaseModel):
    balance: float
    total_earned: float
    total_withdrawn: float
    pending_withdrawal: float


class TransactionItem(BaseModel):
    id: str
    type: str
    amount: float
    description: str
    question_id: Optional[str] = None
    status: str
    created_at: datetime


class WithdrawRequest(BaseModel):
    amount: float
    channel: WithdrawChannel
    account: str

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v < 10.0:
            raise ValueError("最低提现金额为 10 元")
        return v


class WithdrawResponse(BaseModel):
    withdrawal_id: str
    amount: float
    channel: str
    status: str
    estimated_completion: datetime
    message: str
