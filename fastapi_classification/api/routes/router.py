from fastapi import APIRouter
from .predict import router as predict_router
from .auth import router as auth_router
from .users import router as users_router
from .cases import router as cases_router
from .diagnosis import router as diagnosis_router
from .patients import router as patients_router
from .medical_info import router as medical_info_router
from .images import router as images_router
from .doctor_notes import router as doctor_notes_router

api_router = APIRouter()

# 注册预测路由
api_router.include_router(predict_router, prefix="/predict", tags=["预测"])

# 注册认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 注册用户管理路由
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])

# 注册病例管理路由
api_router.include_router(cases_router, prefix="/cases", tags=["病例管理"])

# 注册诊断管理路由
api_router.include_router(diagnosis_router, prefix="/diagnosis", tags=["诊断管理"])

# 注册患者管理路由
api_router.include_router(patients_router, prefix="/patients", tags=["患者管理"])

# 注册医疗信息路由
api_router.include_router(medical_info_router, prefix="/medical-info", tags=["医疗信息"])

# 注册图片管理路由
api_router.include_router(images_router, prefix="/images", tags=["图片管理"])

# 注册医生笔记路由
api_router.include_router(doctor_notes_router, prefix="/doctor-notes", tags=["医生笔记"])

