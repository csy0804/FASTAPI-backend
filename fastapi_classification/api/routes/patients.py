from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...core.database import get_db, get_mongodb
from ...schemas.medical_info import MedicalInfoResponse, MedicalInfoCreate, MedicalInfoUpdate
from ...core.security import get_current_user
from ...models.user import User
from ...services.database_service import DatabaseService

# 依赖注入函数，提供 DatabaseService 实例
async def get_database_service(
    postgres_db: Session = Depends(get_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
) -> DatabaseService:
    return DatabaseService(postgres_db, mongodb_db)

router = APIRouter()

@router.post("/medical_info/me", response_model=MedicalInfoResponse)
async def create_medical_info(
    info: MedicalInfoCreate,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """创建当前用户的医疗信息"""
    try:
        existing_info = await db_service.get_medical_info(current_user.id)
        if existing_info:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该用户已有医疗信息记录")
    except HTTPException as e:
         if e.status_code != status.HTTP_404_NOT_FOUND:
             raise e

    return await db_service.create_medical_info(info, current_user.id)

@router.get("/medical_info/me", response_model=MedicalInfoResponse)
async def read_my_medical_info(
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的医疗信息"""
    return await db_service.get_medical_info(current_user.id)

@router.put("/medical_info/me", response_model=MedicalInfoResponse)
async def update_my_medical_info(
    info_update: MedicalInfoUpdate,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """更新当前用户的医疗信息"""
    return await db_service.update_medical_info(current_user.id, info_update)

@router.delete("/medical_info/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_medical_info(
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """删除当前用户的医疗信息"""
    await db_service.delete_medical_info(current_user.id)
    return