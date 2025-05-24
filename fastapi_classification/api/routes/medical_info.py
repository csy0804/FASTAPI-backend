from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...core.database import get_db, get_mongodb
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...schemas.medical_info import MedicalInfoCreate, MedicalInfoUpdate, MedicalInfoResponse
from ...services.database_service import DatabaseService
from fastapi import status

router = APIRouter()

# 依赖注入函数，提供 DatabaseService 实例
async def get_database_service(
    postgres_db: Session = Depends(get_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
) -> DatabaseService:
    return DatabaseService(postgres_db, mongodb_db)

@router.post("/", response_model=MedicalInfoResponse)
async def create_medical_info(
    info: MedicalInfoCreate,
    postgres_db: Session = Depends(get_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_user)
):
    """创建医疗信息"""
    db_service = DatabaseService(postgres_db, mongodb_db)
    
    # 检查用户是否已经有医疗信息记录
    try:
        existing_info = await db_service.get_medical_info(current_user.id)
        if existing_info:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该用户已有医疗信息记录")
    except HTTPException as e:
         # 如果是 404 错误表示医疗信息不存在，可以继续创建
         if e.status_code != status.HTTP_404_NOT_FOUND:
             raise e

    return await db_service.create_medical_info(info, current_user.id)

@router.get("/{user_id}", response_model=MedicalInfoResponse)
async def get_medical_info(
    user_id: int,
    postgres_db: Session = Depends(get_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_user)
):
    """获取用户的医疗信息"""
    # 检查权限
    if current_user.id != user_id and current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="无权访问其他用户的医疗信息")
    db_service = DatabaseService(postgres_db, mongodb_db)
    return await db_service.get_medical_info(user_id)

@router.put("/{user_id}", response_model=MedicalInfoResponse)
async def update_medical_info(
    user_id: int,
    info: MedicalInfoUpdate,
    postgres_db: Session = Depends(get_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_user)
):
    """更新医疗信息"""
    # 检查权限
    if current_user.id != user_id and current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="无权修改其他用户的医疗信息")
    db_service = DatabaseService(postgres_db, mongodb_db)
    return await db_service.update_medical_info(user_id, info)

@router.delete("/{user_id}")
async def delete_medical_info(
    user_id: int,
    postgres_db: Session = Depends(get_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_user)
):
    """删除医疗信息"""
    # 检查权限
    if current_user.id != user_id and current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="无权删除其他用户的医疗信息")
    db_service = DatabaseService(postgres_db, mongodb_db)
    await db_service.delete_medical_info(user_id)
    return {"message": "医疗信息已删除"} 