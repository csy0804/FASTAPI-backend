from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...services.auth import get_current_active_user
from ...schemas.user import User, UserUpdate
from ...models.user import User as UserModel, UserRole
from ...core.database import get_db, get_mongodb
from ...services.database_service import DatabaseService

# 依赖注入函数，提供 DatabaseService 实例
async def get_database_service(
    postgres_db: Session = Depends(get_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
) -> DatabaseService:
    return DatabaseService(postgres_db, mongodb_db)

router = APIRouter()

# 获取用户列表（仅管理员）
@router.get("/", response_model=List[User])
async def read_users(
    db_service: DatabaseService = Depends(get_database_service),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="权限不足"
        )
    users = await db_service.get_all_users(skip=skip, limit=limit)
    return users

# 获取指定用户信息
@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    user = await db_service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    # 只有管理员或本人可查看
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="权限不足"
        )
    return user

# 更新用户信息（仅管理员或本人）
@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="权限不足")

    user = await db_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user

# 删除用户（仅管理员）
@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")

    success = await db_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    return status.HTTP_204_NO_CONTENT