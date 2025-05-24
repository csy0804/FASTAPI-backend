from datetime import datetime, timezone
from typing import List, Optional
import json
import logging

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from .cache_service import CacheService
from ..models.case import Case, CaseStatus
from ..models.diagnosis import Diagnosis, DiagnosisStatus, DiagnosisPriority
from ..models.doctor_note import DoctorNote, NoteType
from ..models.user import User, UserRole
from ..models.medical_info import MedicalInfo
from ..schemas.case import CaseCreate, CaseUpdate, CaseResponse
from ..schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate, DiagnosisResponse
from ..schemas.doctor_note import DoctorNoteCreate, DoctorNoteUpdate, DoctorNoteResponse
from ..schemas.medical_info import MedicalInfoCreate, MedicalInfoUpdate, MedicalInfoResponse
from ..schemas.user import UserUpdate
from ..models.image import Image
from ..core.security import get_password_hash

# 配置日志记录器
logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, postgres_db: Session, mongodb_db: AsyncIOMotorDatabase):
        self.postgres_db = postgres_db
        self.mongodb_db = mongodb_db
        self.cache = CacheService()

    # 病例相关方法
    async def create_case(self, case: CaseCreate, user_id: int) -> CaseResponse:
        """创建病例"""
        db_case = Case(
            **case.model_dump(exclude={'status'}),
            created_by=user_id,
        )
        self.postgres_db.add(db_case)
        self.postgres_db.commit()
        self.postgres_db.refresh(db_case)
        return CaseResponse.model_validate(db_case)

    async def get_case(self, case_id: int) -> CaseResponse:
        """获取病例"""
        case = self.postgres_db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="病例不存在")
        return CaseResponse.model_validate(case)

    async def update_case(self, case_id: int, case: CaseUpdate) -> CaseResponse:
        """更新病例"""
        db_case = self.postgres_db.query(Case).filter(Case.id == case_id).first()
        if not db_case:
            raise HTTPException(status_code=404, detail="病例不存在")

        update_data = case.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_case, key, value)

        self.postgres_db.commit()
        self.postgres_db.refresh(db_case)
        return CaseResponse.model_validate(db_case)

    async def get_all_cases(self, skip: int = 0, limit: int = 20) -> List[CaseResponse]:
        """获取所有病例"""
        cases = self.postgres_db.query(Case).offset(skip).limit(limit).all()
        return [CaseResponse.model_validate(case) for case in cases]

    async def get_user_cases(self, user_id: int, skip: int = 0, limit: int = 20) -> List[CaseResponse]:
        """获取用户创建的病例"""
        cases = self.postgres_db.query(Case).filter(
            Case.created_by == user_id
        ).offset(skip).limit(limit).all()
        return [CaseResponse.model_validate(case) for case in cases]

    async def delete_case(self, case_id: int) -> None:
        """删除病例"""
        case = self.postgres_db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="病例不存在")
        
        self.postgres_db.delete(case)
        self.postgres_db.commit()

    # 诊断相关方法
    async def create_diagnosis(self, diagnosis: DiagnosisCreate, case_id: int, doctor_id: int) -> DiagnosisResponse:
        """创建诊断"""
        # 验证病例
        case = self.postgres_db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="病例不存在")

        # 验证医生
        doctor = self.postgres_db.query(User).filter(
            User.id == doctor_id,
            User.role == UserRole.DOCTOR
        ).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="医生不存在")

        db_diagnosis = Diagnosis(
            **diagnosis.model_dump(exclude={'status', 'priority', 'confidence_score'}),
            case_id=case_id,
            doctor_id=doctor_id,
            status=DiagnosisStatus.PENDING,
            priority=DiagnosisPriority.MEDIUM,
            confidence_score=diagnosis.confidence_score if diagnosis.confidence_score is not None else 0.0
        )
        self.postgres_db.add(db_diagnosis)
        self.postgres_db.commit()
        self.postgres_db.refresh(db_diagnosis)
        return DiagnosisResponse.model_validate(db_diagnosis)

    async def get_diagnosis(self, diagnosis_id: int) -> DiagnosisResponse:
        """获取诊断"""
        diagnosis = self.postgres_db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not diagnosis:
            raise HTTPException(status_code=404, detail="诊断不存在")
            
        # 确保 confidence_score 有有效值
        if diagnosis.confidence_score is None:
            diagnosis.confidence_score = 0.0
            
        return DiagnosisResponse.model_validate(diagnosis)

    async def update_diagnosis(self, diagnosis_id: int, diagnosis: DiagnosisUpdate) -> DiagnosisResponse:
        """更新诊断"""
        db_diagnosis = self.postgres_db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not db_diagnosis:
            raise HTTPException(status_code=404, detail="诊断不存在")

        update_data = diagnosis.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_diagnosis, key, value)

        self.postgres_db.commit()
        self.postgres_db.refresh(db_diagnosis)
        return DiagnosisResponse.model_validate(db_diagnosis)

    async def get_case_diagnoses(self, case_id: int) -> List[DiagnosisResponse]:
        """获取病例的所有诊断"""
        # 验证病例
        case = self.postgres_db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="病例不存在")

        # 获取诊断
        diagnoses = self.postgres_db.query(Diagnosis).filter(Diagnosis.case_id == case_id).all()
        
        # 确保每个诊断的 confidence_score 都有有效值
        for diagnosis in diagnoses:
            if diagnosis.confidence_score is None:
                diagnosis.confidence_score = 0.0
                
        return [DiagnosisResponse.model_validate(diagnosis) for diagnosis in diagnoses]

    async def delete_diagnosis(self, diagnosis_id: int) -> None:
        """删除诊断"""
        diagnosis = self.postgres_db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not diagnosis:
            raise HTTPException(status_code=404, detail="诊断不存在")
        
        self.postgres_db.delete(diagnosis)
        self.postgres_db.commit()

    # 医疗信息相关方法
    async def get_medical_info(self, user_id: int) -> MedicalInfoResponse:
        """获取用户医疗信息"""
        # 1. 尝试从缓存获取
        cache_key = f"medical_info:{user_id}"
        cached_data = await self.cache.get_cache(cache_key)
        if cached_data:
            # 缓存中的数据已经是 JSON 格式，_id 应该是字符串
            return MedicalInfoResponse(**cached_data)

        # 2. 从 PostgreSQL 获取用户信息
        user = self.postgres_db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 3. 从 MongoDB 获取医疗信息
        medical_info = await self.mongodb_db.medical_info.find_one({"user_id": user_id})
        if not medical_info:
            raise HTTPException(status_code=404, detail="医疗信息不存在")

        # 手动将 _id 从 ObjectId 转换为字符串，以便 Pydantic 正确处理和存入缓存
        if "_id" in medical_info:
             medical_info["_id"] = str(medical_info["_id"])

        # 4. 存入缓存
        await self.cache.set_cache(cache_key, medical_info)
        return MedicalInfoResponse(**medical_info)

    async def create_medical_info(self, info: MedicalInfoCreate, user_id: int) -> MedicalInfoResponse:
        """创建医疗信息"""
        # 1. 验证用户
        user = self.postgres_db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 2. 创建医疗信息
        medical_info = {
            **info.model_dump(),
            "user_id": user_id,
            "version": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        result = await self.mongodb_db.medical_info.insert_one(medical_info)
        
        # 获取插入的文档，并手动将 _id 从 ObjectId 转换为字符串
        inserted_info = await self.mongodb_db.medical_info.find_one({"_id": result.inserted_id})
        if inserted_info and "_id" in inserted_info:
             inserted_info["_id"] = str(inserted_info["_id"])

        # 3. 清除相关缓存
        await self.cache.delete_cache(f"medical_info:{user_id}")
        
        # 使用转换后的字典创建 MedicalInfoResponse
        return MedicalInfoResponse(**inserted_info)

    async def update_medical_info(self, user_id: int, info: MedicalInfoUpdate) -> MedicalInfoResponse:
        """更新医疗信息"""
        # 1. 验证用户
        user = self.postgres_db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 2. 获取当前版本
        current_info = await self.mongodb_db.medical_info.find_one({"user_id": user_id})
        if not current_info:
            raise HTTPException(status_code=404, detail="医疗信息不存在")

        # 3. 更新信息
        update_data = {
            **info.model_dump(exclude_unset=True),
            "version": current_info["version"] + 1,
            "updated_at": datetime.now(timezone.utc)
        }
        await self.mongodb_db.medical_info.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )

        # 4. 清除相关缓存
        await self.cache.delete_cache(f"medical_info:{user_id}")
        
        # 5. 获取更新后的信息
        updated_info = await self.mongodb_db.medical_info.find_one({"user_id": user_id})
        
        # 手动将 _id 从 ObjectId 转换为字符串，以便 Pydantic 正确处理
        if updated_info and "_id" in updated_info:
             updated_info["_id"] = str(updated_info["_id"])
            
        return MedicalInfoResponse(**updated_info)

    async def delete_medical_info(self, user_id: int) -> None:
        """删除医疗信息"""
        # 1. 验证用户
        user = self.postgres_db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 2. 删除信息
        result = await self.mongodb_db.medical_info.delete_one({"user_id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="医疗信息不存在")

        # 3. 清除相关缓存
        await self.cache.delete_cache(f"medical_info:{user_id}")

    # 医生笔记相关方法
    async def check_doctor_medical_info_access(self, doctor_id: int, medical_info_id: int) -> bool:
        """检查医生是否有权限访问医疗信息"""
        try:
            # 1. 获取医疗信息
            medical_info = self.postgres_db.query(MedicalInfo).filter(
                MedicalInfo.id == medical_info_id
            ).first()
            if not medical_info:
                return False

            # 2. 检查医生是否是病人的主治医生
            case = self.postgres_db.query(Case).filter(
                Case.created_by == medical_info.user_id
            ).first()
            if case:
                # 检查医生是否有该病例的诊断记录
                diagnosis = self.postgres_db.query(Diagnosis).filter(
                    Diagnosis.case_id == case.id,
                    Diagnosis.doctor_id == doctor_id
                ).first()
                if diagnosis:
                    return True

            # 3. 检查医生是否已经有该医疗信息的笔记
            existing_note = self.postgres_db.query(DoctorNote).filter(
                DoctorNote.medical_info_id == medical_info_id,
                DoctorNote.doctor_id == doctor_id
            ).first()
            if existing_note:
                return True

            return False
        except Exception as e:
            logger.error(f"检查医生访问权限时发生错误: {str(e)}")
            return False

    async def create_doctor_note(self, note: DoctorNoteCreate, doctor_id: int) -> DoctorNoteResponse:
        """创建医生笔记"""
        # 1. 验证医生
        doctor = self.postgres_db.query(User).filter(
            User.id == doctor_id,
            User.role == UserRole.DOCTOR
        ).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="医生不存在")

        # 2. 验证医疗信息是否存在
        medical_info = await self.mongodb_db.medical_info.find_one({"user_id": note.medical_info_id})
        if not medical_info:
            raise HTTPException(status_code=404, detail="医疗信息不存在")

        # 3. 验证医生是否有权限访问该医疗信息
        has_access = await self.check_doctor_medical_info_access(doctor_id, note.medical_info_id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限访问该病人的医疗信息"
            )

        # 4. 创建笔记（PostgreSQL）
        db_note = DoctorNote(
            note_content=note.note_content,
            medical_info_id=note.medical_info_id,
            note_type=note.note_type,
            doctor_id=doctor_id
        )
        self.postgres_db.add(db_note)
        self.postgres_db.commit()
        self.postgres_db.refresh(db_note)

        # 5. 同步到 MongoDB
        mongo_note = {
            "note_id": db_note.id,
            "doctor_id": doctor_id,
            "medical_info_id": note.medical_info_id,
            "note_type": note.note_type.value if isinstance(note.note_type, NoteType) else note.note_type,
            "note_content": note.note_content,
            "is_important": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await self.mongodb_db.doctor_notes.insert_one(mongo_note)

        # 6. 准备响应数据
        note_dict = {
            "id": db_note.id,
            "doctor_id": db_note.doctor_id,
            "note_content": db_note.note_content,
            "medical_info_id": db_note.medical_info_id,
            "note_type": db_note.note_type,
            "created_at": db_note.created_at,
            "updated_at": db_note.updated_at,
            "medical_info": None  # 初始化为 None
        }

        # 7. 如果有医疗信息，处理并添加
        if medical_info:
            # 确保 _id 字段存在
            medical_info["_id"] = str(medical_info.get("_id", ""))
            
            # 确保列表字段是列表类型
            for field in ["surgery_history", "medication_history", "physical_exam_records"]:
                if field in medical_info:
                    if isinstance(medical_info[field], str):
                        try:
                            medical_info[field] = json.loads(medical_info[field])
                        except json.JSONDecodeError:
                            medical_info[field] = []
                    elif medical_info[field] is None:
                        medical_info[field] = []
            
            note_dict["medical_info"] = medical_info

        return DoctorNoteResponse.model_validate(note_dict)

    async def get_doctor_note(self, note_id: int) -> DoctorNoteResponse:
        """获取医生笔记"""
        note = self.postgres_db.query(DoctorNote).filter(DoctorNote.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在")

        # 获取关联的医疗信息
        medical_info = await self.mongodb_db.medical_info.find_one({"user_id": note.medical_info_id})
        
        # 准备笔记数据
        note_dict = {
            "id": note.id,
            "doctor_id": note.doctor_id,
            "note_content": note.note_content,
            "medical_info_id": note.medical_info_id,
            "note_type": note.note_type,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "medical_info": None  # 初始化为 None
        }
        
        # 如果有医疗信息，处理并添加
        if medical_info:
            # 确保 _id 字段存在并转换为字符串
            medical_info["_id"] = str(medical_info.get("_id", ""))
            
            # 确保列表字段是列表类型
            for field in ["surgery_history", "medication_history", "physical_exam_records"]:
                if field in medical_info:
                    if isinstance(medical_info[field], str):
                        try:
                            medical_info[field] = json.loads(medical_info[field])
                        except json.JSONDecodeError:
                            medical_info[field] = []
                    elif medical_info[field] is None:
                        medical_info[field] = []
                    elif not isinstance(medical_info[field], list):
                        medical_info[field] = []
            
            # 确保所有必需的字段都存在
            medical_info.setdefault("medical_history", "")
            medical_info.setdefault("allergy_history", "")
            medical_info.setdefault("family_history", "")
            medical_info.setdefault("version", 1)
            medical_info.setdefault("created_at", datetime.now(timezone.utc))
            medical_info.setdefault("updated_at", datetime.now(timezone.utc))
            
            # 将 medical_info 转换为字典格式，确保字段类型正确
            medical_info_dict = {
                "_id": str(medical_info["_id"]),  # 确保 _id 是字符串
                "user_id": int(medical_info["user_id"]),  # 确保 user_id 是整数
                "medical_history": str(medical_info["medical_history"]),
                "allergy_history": str(medical_info["allergy_history"]),
                "family_history": str(medical_info["family_history"]),
                "surgery_history": medical_info["surgery_history"] if isinstance(medical_info["surgery_history"], list) else [],
                "medication_history": medical_info["medication_history"] if isinstance(medical_info["medication_history"], list) else [],
                "physical_exam_records": medical_info["physical_exam_records"] if isinstance(medical_info["physical_exam_records"], list) else [],
                "version": int(medical_info["version"]),
                "created_at": medical_info["created_at"],
                "updated_at": medical_info["updated_at"]
            }
            
            note_dict["medical_info"] = medical_info_dict
        
        return DoctorNoteResponse.model_validate(note_dict)

    async def update_doctor_note(self, note_id: int, note: DoctorNoteUpdate) -> DoctorNoteResponse:
        """更新医生笔记"""
        # 1. 获取并验证笔记
        db_note = self.postgres_db.query(DoctorNote).filter(DoctorNote.id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="笔记不存在")

        # 2. 更新 PostgreSQL 数据
        update_data = note.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_note, key, value)
        db_note.updated_at = datetime.now(timezone.utc)

        self.postgres_db.commit()
        self.postgres_db.refresh(db_note)

        # 3. 同步到 MongoDB
        try:
            # 构建 MongoDB 更新数据
            mongo_update = {}
            if "note_content" in update_data:
                mongo_update["note_content"] = db_note.note_content
            if "note_type" in update_data:
                mongo_update["note_type"] = db_note.note_type.value if isinstance(db_note.note_type, NoteType) else db_note.note_type
            mongo_update["updated_at"] = db_note.updated_at

            # 执行 MongoDB 更新
            if mongo_update:
                # 先检查文档是否存在
                existing_note = await self.mongodb_db.doctor_notes.find_one({"note_id": note_id})
                if existing_note:
                    result = await self.mongodb_db.doctor_notes.update_one(
                        {"note_id": note_id},
                        {"$set": mongo_update}
                    )
                    if result.modified_count > 0:
                        logger.info(f"成功同步笔记到 MongoDB: {note_id}")
                    else:
                        logger.warning(f"MongoDB 更新未修改任何文档: {note_id}")
                else:
                    # 如果文档不存在，创建新文档
                    mongo_note = {
                        "note_id": note_id,
                        "doctor_id": db_note.doctor_id,
                        "medical_info_id": db_note.medical_info_id,
                        "note_type": db_note.note_type.value if isinstance(db_note.note_type, NoteType) else db_note.note_type,
                        "note_content": db_note.note_content,
                        "is_important": False,
                        "created_at": db_note.created_at,
                        "updated_at": db_note.updated_at
                    }
                    await self.mongodb_db.doctor_notes.insert_one(mongo_note)
                    logger.info(f"在 MongoDB 中创建新笔记: {note_id}")
        except Exception as e:
            logger.error(f"同步笔记到 MongoDB 时发生错误: {str(e)}")
            # 这里我们不抛出异常，因为 PostgreSQL 的更新已经成功
            # 但记录错误日志以便后续处理

        # 4. 获取关联的医疗信息
        medical_info = await self.mongodb_db.medical_info.find_one({"user_id": db_note.medical_info_id})
        
        # 5. 准备响应数据
        note_dict = {
            "id": db_note.id,
            "doctor_id": db_note.doctor_id,
            "note_content": db_note.note_content,
            "medical_info_id": db_note.medical_info_id,
            "note_type": db_note.note_type,
            "created_at": db_note.created_at,
            "updated_at": db_note.updated_at,
            "medical_info": None
        }

        # 6. 处理医疗信息
        if medical_info:
            # 确保 _id 字段存在
            medical_info["_id"] = str(medical_info.get("_id", ""))
            
            # 确保列表字段是列表类型
            for field in ["surgery_history", "medication_history", "physical_exam_records"]:
                if field in medical_info:
                    if isinstance(medical_info[field], str):
                        try:
                            medical_info[field] = json.loads(medical_info[field])
                        except json.JSONDecodeError:
                            medical_info[field] = []
                    elif medical_info[field] is None:
                        medical_info[field] = []
            
            note_dict["medical_info"] = medical_info

        return DoctorNoteResponse.model_validate(note_dict)

    async def delete_doctor_note(self, note_id: int) -> None:
        """删除医生笔记"""
        # 1. 获取并验证笔记
        note = self.postgres_db.query(DoctorNote).filter(DoctorNote.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在")
        
        # 2. 从 PostgreSQL 删除
        self.postgres_db.delete(note)
        self.postgres_db.commit()

        # 3. 从 MongoDB 删除
        try:
            result = await self.mongodb_db.doctor_notes.delete_one({"note_id": note_id})
            if result.deleted_count == 0:
                logger.warning(f"在 MongoDB 中未找到要删除的笔记: {note_id}")
        except Exception as e:
            logger.error(f"从 MongoDB 删除笔记时发生错误: {str(e)}")
            # 这里我们不抛出异常，因为 PostgreSQL 的删除已经成功
            # 但记录错误日志以便后续处理

    async def get_doctor_notes(self, doctor_id: int, skip: int = 0, limit: int = 20) -> List[DoctorNoteResponse]:
        """获取医生的所有笔记"""
        notes = self.postgres_db.query(DoctorNote).filter(
            DoctorNote.doctor_id == doctor_id
        ).offset(skip).limit(limit).all()
        
        # 转换每个笔记为响应模型
        response_notes = []
        for note in notes:
            # 获取关联的医疗信息
            medical_info = await self.mongodb_db.medical_info.find_one({"user_id": note.medical_info_id})
            if medical_info:
                # 确保 _id 字段存在
                medical_info["_id"] = str(medical_info.get("_id", ""))
                
                # 确保列表字段是列表类型
                for field in ["surgery_history", "medication_history", "physical_exam_records"]:
                    if field in medical_info and isinstance(medical_info[field], str):
                        try:
                            medical_info[field] = json.loads(medical_info[field])
                        except json.JSONDecodeError:
                            medical_info[field] = []
            
            # 创建响应对象
            note_dict = {
                "id": note.id,
                "doctor_id": note.doctor_id,
                "note_content": note.note_content,  # 使用 note_content
                "medical_info_id": note.medical_info_id,
                "note_type": note.note_type,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
                "medical_info": medical_info
            }
            response_notes.append(DoctorNoteResponse.model_validate(note_dict))
        
        return response_notes

    async def get_medical_info_notes(self, medical_info_id: int) -> List[DoctorNoteResponse]:
        """获取特定医疗信息的所有医生笔记"""
        notes = self.postgres_db.query(DoctorNote).filter(
            DoctorNote.medical_info_id == medical_info_id
        ).all()
        
        # 转换每个笔记为响应模型
        response_notes = []
        for note in notes:
            # 获取关联的医疗信息
            medical_info = await self.mongodb_db.medical_info.find_one({"user_id": note.medical_info_id})
            
            # 准备笔记数据
            note_dict = {
                "id": note.id,
                "doctor_id": note.doctor_id,
                "note_content": note.note_content,
                "medical_info_id": note.medical_info_id,
                "note_type": note.note_type,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
                "medical_info": None  # 初始化为 None
            }
            
            # 如果有医疗信息，处理并添加
            if medical_info:
                # 确保 _id 字段存在
                medical_info["_id"] = str(medical_info.get("_id", ""))
                
                # 确保列表字段是列表类型
                for field in ["surgery_history", "medication_history", "physical_exam_records"]:
                    if field in medical_info:
                        if isinstance(medical_info[field], str):
                            try:
                                medical_info[field] = json.loads(medical_info[field])
                            except json.JSONDecodeError:
                                medical_info[field] = []
                        elif medical_info[field] is None:
                            medical_info[field] = []
                
                note_dict["medical_info"] = medical_info
            
            response_notes.append(DoctorNoteResponse.model_validate(note_dict))
        
        return response_notes

    # 图片相关方法
    async def create_image(self, image: Image) -> Image:
        """创建图片记录"""
        result = await self.mongodb_db.images.insert_one(image.model_dump())
        image.id = str(result.inserted_id)
        return image

    async def get_image(self, image_id: str) -> Optional[Image]:
        """获取图片记录"""
        from bson import ObjectId # 在函数内部导入以避免循环导入
        try:
            # 尝试将 image_id 转换为 ObjectId
            object_id = ObjectId(image_id)
        except:
            # 如果转换失败，说明 image_id 不是有效的 ObjectId 字符串
            return None

        image_data = await self.mongodb_db.images.find_one({"_id": object_id})
        if image_data:
            return Image(**image_data)
        return None

    async def delete_image(self, image_id: str) -> bool:
        """删除图片记录"""
        from bson import ObjectId # 在函数内部导入以避免循环导入
        try:
            object_id = ObjectId(image_id)
        except:
            return False # 无效的 image_id

        result = await self.mongodb_db.images.delete_one({"_id": object_id})
        return result.deleted_count > 0

    async def get_user_images(self, user_id: int) -> List[Image]:
        """获取用户的所有图片记录"""
        cursor = self.mongodb_db.images.find({"user_id": user_id})
        images_data = await cursor.to_list(length=None)
        return [Image(**image_data) for image_data in images_data]

    async def get_case_images(self, case_id: int) -> List[Image]:
        """获取病例相关的所有图片记录"""
        cursor = self.mongodb_db.images.find({"case_id": case_id})
        images_data = await cursor.to_list(length=None)
        return [Image(**image_data) for image_data in images_data]

    async def get_diagnosis_images(self, diagnosis_id: int) -> List[Image]:
        """获取诊断相关的所有图片记录"""
        cursor = self.mongodb_db.images.find({"diagnosis_id": diagnosis_id})
        images_data = await cursor.to_list(length=None)
        return [Image(**image_data) for image_data in images_data]

    # 用户相关方法
    async def get_user(self, user_id: int) -> Optional[User]:
        """根据用户ID获取用户"""
        return self.postgres_db.query(User).filter(User.id == user_id).first()

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户列表"""
        return self.postgres_db.query(User).offset(skip).limit(limit).all()

    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = self.postgres_db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        
        # 如果更新包含密码，需要先进行哈希处理
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])
            
        for key, value in update_data.items():
            setattr(db_user, key, value)

        self.postgres_db.commit()
        self.postgres_db.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        db_user = self.postgres_db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        self.postgres_db.delete(db_user)
        self.postgres_db.commit()
        return True 