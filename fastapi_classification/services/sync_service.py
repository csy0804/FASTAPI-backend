import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from ..models.diagnosis import Diagnosis, DiagnosisStatus, DiagnosisPriority
from ..models.doctor_note import DoctorNote, NoteType
from ..models.mongodb_models import (
    MongoMedicalInfo, 
    MongoDoctorNote, 
    MongoDiagnosisDetail,
    PrivacyLevel
)
from ..models.user import User
from ..models.case import Case, CaseStatus

logger = logging.getLogger(__name__)

class SyncService:
    def __init__(self, postgres_db: Session, mongo_db: AsyncIOMotorDatabase) -> None:
        self.postgres_db = postgres_db
        self.mongo_db = mongo_db

    async def sync_medical_info(self, user_id: int) -> MongoMedicalInfo:
        """同步用户医疗信息"""
        try:
            # 检查用户是否存在
            user = self.postgres_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")

            # 检查MongoDB中是否存在该用户的医疗信息
            existing_info = await self.mongo_db.medical_info.find_one({"user_id": user_id})
            if not existing_info:
                # 创建新的医疗信息记录
                medical_info = MongoMedicalInfo(
                    user_id=user_id,
                    medical_history="",
                    allergy_history="",
                    family_history="",
                    surgery_history=[],
                    medication_history=[],
                    physical_exam_records=[],
                    privacy_level=PrivacyLevel.DOCTORS_ONLY,
                    version=1,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                result = await self.mongo_db.medical_info.insert_one(medical_info.model_dump())
                medical_info.id = str(result.inserted_id)
                logger.info(f"为用户 {user_id} 创建了新的医疗信息记录")
                return medical_info

            # 更新现有记录的时间戳
            await self.mongo_db.medical_info.update_one(
                {"user_id": user_id},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
            return MongoMedicalInfo(**existing_info)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"同步用户 {user_id} 医疗信息时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"同步医疗信息失败: {str(e)}")

    async def sync_diagnosis_detail(self, diagnosis_id: int) -> MongoDiagnosisDetail:
        """同步诊断详情"""
        try:
            # 检查诊断是否存在
            diagnosis = self.postgres_db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
            if not diagnosis:
                raise HTTPException(status_code=404, detail=f"诊断 {diagnosis_id} 不存在")

            # 检查MongoDB中是否存在该诊断的详情
            existing_detail = await self.mongo_db.diagnosis_details.find_one({"diagnosis_id": diagnosis_id})
            if not existing_detail:
                # 创建新的诊断详情记录
                diagnosis_detail = MongoDiagnosisDetail(
                    diagnosis_id=diagnosis_id,
                    case_id=diagnosis.case_id,
                    doctor_id=diagnosis.doctor_id,
                    symptoms={},
                    treatment_plan=diagnosis.treatment_plan if diagnosis.treatment_plan is not None else "",
                    follow_up_notes="",
                    analysis={
                        "confidence_score": float(diagnosis.confidence_score) if diagnosis.confidence_score is not None else 0.0,
                        "supporting_evidence": []
                    },
                    status=diagnosis.status.value if isinstance(diagnosis.status, DiagnosisStatus) else diagnosis.status,
                    priority=diagnosis.priority.value if isinstance(diagnosis.priority, DiagnosisPriority) else diagnosis.priority,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                result = await self.mongo_db.diagnosis_details.insert_one(diagnosis_detail.model_dump())
                diagnosis_detail.id = str(result.inserted_id)
                logger.info(f"为诊断 {diagnosis_id} 创建了新的详情记录")
                return diagnosis_detail

            # 更新现有记录的时间戳和状态
            await self.mongo_db.diagnosis_details.update_one(
                {"diagnosis_id": diagnosis_id},
                {
                    "$set": {
                        "updated_at": datetime.now(timezone.utc),
                        "status": diagnosis.status.value if isinstance(diagnosis.status, DiagnosisStatus) else diagnosis.status,
                        "priority": diagnosis.priority.value if isinstance(diagnosis.priority, DiagnosisPriority) else diagnosis.priority
                    }
                }
            )
            return MongoDiagnosisDetail(**existing_detail)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"同步诊断 {diagnosis_id} 详情时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"同步诊断详情失败: {str(e)}")

    async def sync_doctor_note(self, note_id: int) -> MongoDoctorNote:
        """同步医生笔记"""
        try:
            # 检查笔记是否存在
            note = self.postgres_db.query(DoctorNote).filter(DoctorNote.id == note_id).first()
            if not note:
                raise HTTPException(status_code=404, detail=f"笔记 {note_id} 不存在")

            # 检查MongoDB中是否存在该笔记
            existing_note = await self.mongo_db.doctor_notes.find_one({"note_id": note_id})
            if not existing_note:
                # 创建新的笔记记录
                doctor_note = MongoDoctorNote(
                    note_id=note_id,
                    doctor_id=note.doctor_id,
                    medical_info_id=note.medical_info_id,
                    case_id=note.case_id,
                    note_type=note.note_type.value if isinstance(note.note_type, NoteType) else note.note_type,
                    note_content=note.note_content,
                    is_important=note.is_important,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                result = await self.mongo_db.doctor_notes.insert_one(doctor_note.model_dump())
                doctor_note.id = str(result.inserted_id)
                logger.info(f"为笔记 {note_id} 创建了新的记录")
                return doctor_note

            # 更新现有记录的时间戳
            await self.mongo_db.doctor_notes.update_one(
                {"note_id": note_id},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
            return MongoDoctorNote(**existing_note)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"同步笔记 {note_id} 时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"同步医生笔记失败: {str(e)}")

    async def sync_case(self, case_id: int) -> Dict[str, Any]:
        """同步病例数据"""
        try:
            # 检查病例是否存在
            case = self.postgres_db.query(Case).filter(Case.id == case_id).first()
            if not case:
                raise HTTPException(status_code=404, detail=f"病例 {case_id} 不存在")

            # 同步相关数据
            medical_info = await self.sync_medical_info(case.created_by)
            diagnoses = self.postgres_db.query(Diagnosis).filter(Diagnosis.case_id == case_id).all()
            diagnosis_details = []
            for diagnosis in diagnoses:
                detail = await self.sync_diagnosis_detail(diagnosis.id)
                diagnosis_details.append(detail)

            notes = self.postgres_db.query(DoctorNote).filter(DoctorNote.case_id == case_id).all()
            doctor_notes = []
            for note in notes:
                note_detail = await self.sync_doctor_note(note.id)
                doctor_notes.append(note_detail)

            return {
                "case": {
                    "id": case.id,
                    "status": case.status.value if isinstance(case.status, CaseStatus) else case.status,
                    "created_at": case.created_at,
                    "updated_at": case.updated_at
                },
                "medical_info": medical_info.model_dump() if medical_info else None,
                "diagnoses": [d.model_dump() for d in diagnosis_details if d] if diagnosis_details else [],
                "doctor_notes": [n.model_dump() for n in doctor_notes if n] if doctor_notes else []
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"同步病例 {case_id} 时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"同步病例数据失败: {str(e)}")

    async def sync_all_data(self) -> Dict[str, int]:
        """同步所有数据"""
        logger.info("开始同步数据...")
        stats = {
            "medical_info": 0,
            "diagnoses": 0,
            "doctor_notes": 0,
            "cases": 0
        }
        
        try:
            # 同步用户医疗信息
            users = self.postgres_db.query(User).all()
            for user in users:
                try:
                    await self.sync_medical_info(user.id)
                    stats["medical_info"] += 1
                except HTTPException as e:
                     logger.warning(f"同步用户 {user.id} 医疗信息失败: {e.detail}")
                except Exception as e:
                     logger.error(f"同步用户 {user.id} 医疗信息时发生未知错误: {str(e)}")
            
            # 同步病例
            cases = self.postgres_db.query(Case).all()
            for case in cases:
                try:
                    await self.sync_case(case.id)
                    stats["cases"] += 1
                except HTTPException as e:
                     logger.warning(f"同步病例 {case.id} 失败: {e.detail}")
                except Exception as e:
                     logger.error(f"同步病例 {case.id} 时发生未知错误: {str(e)}")
            
            # 同步诊断详情 (已经在 sync_case 中处理)
            # 同步医生笔记 (已经在 sync_case 中处理)
            
            logger.info(f"数据同步完成！统计信息: {stats}")
            return stats

        except Exception as e:
            logger.error(f"同步数据时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"同步数据失败: {str(e)}")

# 移除 None 实例，依赖注入会负责初始化
# sync_service = SyncService(None, None) 