from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.redis_client import get_redis, close_redis
from app.routers import auth, users, questions, comments, favorites, notes, ai, subscriptions, wallet, meta, rankings

app = FastAPI(
    title="OfferPilot API",
    description="互联网大厂面试备战平台 API V1",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 统一 HTTPException 响应格式
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": str(detail), "data": None},
    )


# Pydantic 校验错误 -> 统一 40002
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0]["msg"] if errors else "参数校验失败"
    return JSONResponse(
        status_code=422,
        content={"code": 40002, "message": f"参数校验失败: {msg}", "data": None},
    )


# 兜底 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 50001, "message": "服务器内部错误", "data": None},
    )


# Lifecycle
@app.on_event("startup")
async def startup():
    await get_redis()


@app.on_event("shutdown")
async def shutdown():
    await close_redis()


# Register routers under /v1
PREFIX = "/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(questions.router, prefix=PREFIX)
app.include_router(comments.router, prefix=PREFIX)
app.include_router(favorites.router, prefix=PREFIX)
app.include_router(notes.router, prefix=PREFIX)
app.include_router(ai.router, prefix=PREFIX)
app.include_router(subscriptions.router, prefix=PREFIX)
app.include_router(wallet.router, prefix=PREFIX)
app.include_router(meta.router, prefix=PREFIX)
app.include_router(rankings.router, prefix=PREFIX)


@app.get("/", tags=["健康检查"])
async def root():
    return {"code": 0, "message": "OfferPilot API is running", "version": "1.0.0"}


@app.get("/health", tags=["健康检查"])
async def health():
    return {"status": "ok"}
