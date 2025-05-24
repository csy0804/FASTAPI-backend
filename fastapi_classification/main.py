from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_classification.core.config import settings
from fastapi_classification.core.redis import redis_manager
from fastapi_classification.core.mongodb import mongodb, close_mongo_connection
from fastapi_classification.api.routes.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化 Redis"""
    await redis_manager.init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时关闭 Redis 连接"""
    await redis_manager.close()
    await close_mongo_connection()
