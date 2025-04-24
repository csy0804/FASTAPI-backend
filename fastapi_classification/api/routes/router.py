from fastapi import APIRouter
from .predict import router as predict_router
from .auth import router as auth_router
from .users import router as users_router
from .cases import router as cases_router
api_router = APIRouter()

# 注册预测路由
api_router.include_router(predict_router, prefix="/predict", tags=["预测"])

# 注册认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 注册用户管理路由
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])

# 注册病例管理路由
api_router.include_router(cases_router, prefix="/cases", tags=["病例管理"])