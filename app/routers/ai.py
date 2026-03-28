from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import Response
from app.schemas.ai import AiAnswerRequest
from app.services.ai_service import AiService
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/answer", summary="生成 AI 参考答案（SSE 流式）")
async def generate_ai_answer(
    body: AiAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    generator = AiService.stream_answer(db, user_id, body.question_id)
    return StreamingResponse(generator, media_type="text/event-stream")


@router.get("/answer/{question_id}", summary="获取历史 AI 答案")
async def get_ai_answer_history(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await AiService.get_cached_answer(db, user_id, question_id)
    return Response.ok(result)
