from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from ...core.database import get_postgres_db, get_mongodb
from ...schemas.doctor_note import DoctorNoteCreate, DoctorNoteUpdate, DoctorNoteResponse, NoteType
from ...core.security import get_current_doctor
from ...models.user import User
from ...services.database_service import DatabaseService
from ...models.user import UserRole

# 依赖注入函数，提供 DatabaseService 实例
async def get_database_service(
    postgres_db: Session = Depends(get_postgres_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
) -> DatabaseService:
    # postgres_db 已经是一个 Session 对象，不需要额外处理
    return DatabaseService(postgres_db, mongodb_db)

router = APIRouter()

@router.get("/doctor/{doctor_id}", response_model=List[DoctorNoteResponse]) # 修改路径以更清晰
async def get_doctor_notes(
    doctor_id: int,
    db_service: DatabaseService = Depends(get_database_service), # 使用依赖注入获取 DatabaseService
    current_user: User = Depends(get_current_doctor)
):
    """获取医生的所有笔记"""
    # 检查权限：只允许医生查看自己的笔记
    if current_user.id != doctor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问其他医生的笔记")
    # 医生可以查看自己的所有笔记，不需要 medical_info_id 过滤
    return await db_service.get_doctor_notes(doctor_id)

@router.post("/", response_model=DoctorNoteResponse)
async def create_doctor_note(
    note: DoctorNoteCreate,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_doctor)
):
    """创建医生笔记"""
    try:
        # 1. 验证医生权限
        if current_user.role != UserRole.DOCTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有医生可以创建笔记"
            )

        # 2. 验证笔记类型
        if note.note_type not in [t.value for t in NoteType]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的笔记类型。有效类型：{', '.join([t.value for t in NoteType])}"
            )

        # 3. 验证笔记内容
        if not note.note_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="笔记内容不能为空"
            )

        # 4. 创建笔记
        return await db_service.create_doctor_note(note, current_user.id)
    except HTTPException as e:
        # 直接重新抛出 HTTP 异常
        raise e
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建笔记时发生错误：{str(e)}"
        )

@router.get("/medical-info/{medical_info_id}", response_model=List[DoctorNoteResponse])
async def get_medical_info_notes(
    medical_info_id: int,
    db_service: DatabaseService = Depends(get_database_service), # 使用依赖注入获取 DatabaseService
    current_user: User = Depends(get_current_doctor) # 只有医生可以访问与医疗信息相关的笔记
):
    """获取特定医疗信息的所有笔记"""
    # 在服务层已经根据 medical_info_id 获取笔记
    # 如果需要更精细的权限控制（例如只有与该医疗信息相关的医生才能查看），可以在服务层或这里添加检查
    # 例如：检查获取到的笔记列表中是否有当前医生的笔记，或者检查当前医生是否与该 medical_info 关联的 patient/case 相关联
    # 当前实现允许任何医生查看与特定 medical_info 相关的笔记
    return await db_service.get_medical_info_notes(medical_info_id)

@router.put("/{note_id}", response_model=DoctorNoteResponse)
async def update_doctor_note(
    note_id: int, # 注意：这里 note_id 应该是 int 类型，因为在 models 中定义为 Integer
    note_update: DoctorNoteUpdate,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_doctor)
):
    """更新医生笔记"""
    # 检查权限：只有笔记的作者可以更新笔记
    note = await db_service.get_doctor_note(note_id)
    if not note or note.doctor_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权更新此笔记")
    
    return await db_service.update_doctor_note(note_id, note_update)

@router.delete("/{note_id}")
async def delete_doctor_note(
    note_id: int, # 注意：这里 note_id 应该是 int 类型
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_doctor)
):
    """删除医生笔记"""
    # 检查权限：只有笔记的作者可以删除笔记
    note = await db_service.get_doctor_note(note_id)
    if not note or note.doctor_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此笔记")
         
    await db_service.delete_doctor_note(note_id)
    return {"message": "医生笔记已删除"} 