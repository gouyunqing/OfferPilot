from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.services.meta_service import MetaService

router = APIRouter(prefix="/meta", tags=["基础数据"])


@router.get("/companies", summary="获取公司列表")
async def get_companies(db: AsyncSession = Depends(get_db)):
    result = await MetaService.get_companies(db)
    return Response.ok(result)


@router.get("/positions", summary="获取岗位列表")
async def get_positions(db: AsyncSession = Depends(get_db)):
    result = await MetaService.get_positions(db)
    return Response.ok(result)


@router.get("/rounds", summary="获取面试轮次列表")
async def get_rounds():
    result = MetaService.get_rounds()
    return Response.ok(result)


@router.get("/companies/stats", summary="获取公司题目统计")
async def get_company_stats(db: AsyncSession = Depends(get_db)):
    result = await MetaService.get_company_stats(db)
    return Response.ok(result)
