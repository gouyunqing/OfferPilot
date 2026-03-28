from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: float
    period_months: int
    auto_renew: bool
    apple_product_id: str
    discount_label: Optional[str] = None
    original_price: float


class SubscriptionPlansResponse(BaseModel):
    plans: List[SubscriptionPlan]


class AppleVerifyRequest(BaseModel):
    receipt_data: str
    transaction_id: str
    product_id: str


class SubscriptionInfo(BaseModel):
    id: str
    plan: str
    status: str
    starts_at: datetime
    expires_at: datetime
    auto_renew: bool


class AppleVerifyResponse(BaseModel):
    subscription: SubscriptionInfo
    message: str


class SubscriptionStatusResponse(BaseModel):
    is_member: bool
    is_trial: bool
    plan: Optional[str] = None
    status: Optional[str] = None
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    auto_renew: bool = False
    trial_ends_at: Optional[datetime] = None
