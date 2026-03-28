from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.schemas.wallet import WithdrawRequest
from app.services.wallet_service import WalletService
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/wallet", tags=["钱包"])


@router.get("", summary="获取钱包信息")
async def get_wallet(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await WalletService.get_wallet(db, user_id)
    return Response.ok(result)


@router.get("/transactions", summary="获取收支明细")
async def get_transactions(
    type: Optional[str] = Query("all", pattern="^(reward|withdraw|all)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await WalletService.get_transactions(db, user_id, type, page, page_size)
    return Response.ok(result)


@router.post("/withdraw", summary="发起提现")
async def withdraw(
    body: WithdrawRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await WalletService.withdraw(db, user_id, body)
    return Response.ok(result)


@router.get("/withdrawals", summary="获取提现记录")
async def get_withdrawals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await WalletService.get_withdrawals(db, user_id, page, page_size)
    return Response.ok(result)
