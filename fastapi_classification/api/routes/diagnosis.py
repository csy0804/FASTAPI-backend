from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...core.database import get_db, get_mongodb
from ...models.user import User, UserRole
from ...schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate, DiagnosisResponse
from ...core.security import get_current_doctor, get_current_user
from ...services.database_service import DatabaseService

# 依赖注入函数，提供 DatabaseService 实例
async def get_database_service(
    postgres_db: Session = Depends(get_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
) -> DatabaseService:
    return DatabaseService(postgres_db, mongodb_db)

router = APIRouter()

@router.post("/cases/{case_id}", response_model=DiagnosisResponse)
async def create_diagnosis(
    case_id: int,
    diagnosis: DiagnosisCreate,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_doctor)
):
    """创建诊断记录"""
    return await db_service.create_diagnosis(diagnosis, case_id, current_user.id)

@router.get("/cases/{case_id}", response_model=List[DiagnosisResponse])
async def get_case_diagnoses(
    case_id: int,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """获取病例的所有诊断记录"""
    case = await db_service.get_case(case_id)
    if current_user.role != UserRole.DOCTOR and case.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此病例的诊断")
    
    return await db_service.get_case_diagnoses(case_id)

@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    diagnosis_id: int,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """获取单个诊断记录"""
    diagnosis = await db_service.get_diagnosis(diagnosis_id)
    
    if current_user.role != UserRole.DOCTOR:
        case = await db_service.get_case(diagnosis.case_id)
        if case.created_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此诊断")
             
    return diagnosis

@router.put("/{diagnosis_id}", response_model=DiagnosisResponse)
async def update_diagnosis(
    diagnosis_id: int,
    diagnosis_update: DiagnosisUpdate,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_doctor)
):
    """更新诊断记录"""
    diagnosis = await db_service.get_diagnosis(diagnosis_id)
    if not diagnosis or diagnosis.doctor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权更新此诊断")
         
    return await db_service.update_diagnosis(diagnosis_id, diagnosis_update)

@router.delete("/{diagnosis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diagnosis(
    diagnosis_id: int,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_doctor)
):
    """删除诊断记录"""
    diagnosis = await db_service.get_diagnosis(diagnosis_id)
    if not diagnosis or diagnosis.doctor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此诊断")

    await db_service.delete_diagnosis(diagnosis_id)
    return 