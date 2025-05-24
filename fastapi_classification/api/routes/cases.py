from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...core.database import get_db, get_mongodb
from ...models.user import User, UserRole
from ...schemas.case import CaseCreate, CaseUpdate, CaseResponse
from ...core.security import get_current_doctor, get_current_user
from ...services.database_service import DatabaseService

router = APIRouter()

# 依赖注入函数，提供 DatabaseService 实例
async def get_database_service(
    postgres_db: Session = Depends(get_db), # 直接依赖 get_db
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
) -> DatabaseService:
    return DatabaseService(postgres_db, mongodb_db)



@router.post("/", response_model=CaseResponse)
async def create_case(
    case: CaseCreate,
    db_service: DatabaseService = Depends(get_database_service), # 使用依赖注入获取 DatabaseService
    current_user: User = Depends(get_current_user) # 假设普通用户也能创建病例，如果只有医生能创建则改回 get_current_doctor
):
    """创建病例"""
    # 如果只有医生能创建，这里可以添加检查：if current_user.role != UserRole.DOCTOR:
    #     raise HTTPException(status_code=403, detail="只有医生才能创建病例")
    return await db_service.create_case(case, current_user.id)

@router.get("/", response_model=List[CaseResponse])
async def list_cases(
    skip: int = 0,
    limit: int = 20,
    db_service: DatabaseService = Depends(get_database_service), # 使用依赖注入获取 DatabaseService
    current_user: User = Depends(get_current_user)
):
    """获取病例列表"""
    # 医生可以查看所有病例，其他用户只能查看自己创建的病例
    if current_user.role == UserRole.DOCTOR:
        return await db_service.get_all_cases(skip, limit)
    else:
        return await db_service.get_user_cases(current_user.id, skip, limit)

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    db_service: DatabaseService = Depends(get_database_service), # 使用依赖注入获取 DatabaseService
    current_user: User = Depends(get_current_user)
):
    """获取单个病例"""
    case = await db_service.get_case(case_id)
    
    # 检查权限：只有医生或病例创建者可以查看
    if current_user.role != UserRole.DOCTOR and case.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限查看此病例")
    
    return case

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    case_update: CaseUpdate, # 参数名修改为 case_update 更清晰
    db_service: DatabaseService = Depends(get_database_service), # 使用依赖注入获取 DatabaseService
    current_user: User = Depends(get_current_user) # 假设病例创建者也能更新，如果只有医生能更新则改回 get_current_doctor
):
    """更新病例"""
    # 检查权限：只有医生或病例创建者可以更新
    case = await db_service.get_case(case_id)
    if current_user.role != UserRole.DOCTOR and case.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限更新此病例")
        
    return await db_service.update_case(case_id, case_update)

@router.delete("/{case_id}")
async def delete_case(
    case_id: int,
    db_service: DatabaseService = Depends(get_database_service), # 使用依赖注入获取 DatabaseService
    current_user: User = Depends(get_current_user) # 假设病例创建者也能删除，如果只有医生能删除则改回 get_current_doctor
):
    """删除病例"""
    # 检查权限：只有医生或病例创建者可以删除
    case = await db_service.get_case(case_id)
    if current_user.role != UserRole.DOCTOR and case.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限删除此病例")

    await db_service.delete_case(case_id)
    return {"message": "病例已删除"}