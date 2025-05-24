from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi_classification.models.mongodb_models import MongoMedicalInfo, MongoDoctorNote, MongoDiagnosisDetail
from datetime import datetime, timezone

# 医疗信息 CRUD 操作
async def create_medical_info(db: AsyncIOMotorDatabase, medical_info: MongoMedicalInfo) -> str:
    result = await db.medical_info.insert_one(medical_info.model_dump())
    return str(result.inserted_id)

async def get_medical_info(db: AsyncIOMotorDatabase, user_id: int) -> Optional[Dict[str, Any]]:
    return await db.medical_info.find_one({"user_id": user_id})

async def update_medical_info(db: AsyncIOMotorDatabase, user_id: int, medical_info: Dict[str, Any]) -> bool:
    medical_info["updated_at"] = datetime.now(timezone.utc)
    result = await db.medical_info.update_one(
        {"user_id": user_id},
        {"$set": medical_info}
    )
    return result.modified_count > 0

async def delete_medical_info(db: AsyncIOMotorDatabase, user_id: int) -> bool:
    result = await db.medical_info.delete_one({"user_id": user_id})
    return result.deleted_count > 0

# 医生笔记 CRUD 操作
async def create_doctor_note(db: AsyncIOMotorDatabase, note: MongoDoctorNote) -> str:
    result = await db.doctor_notes.insert_one(note.model_dump())
    return str(result.inserted_id)

async def get_doctor_notes(db: AsyncIOMotorDatabase, medical_info_id: int) -> List[Dict[str, Any]]:
    cursor = db.doctor_notes.find({"medical_info_id": medical_info_id})
    return await cursor.to_list(length=None)

async def update_doctor_note(db: AsyncIOMotorDatabase, note_id: str, note: Dict[str, Any]) -> bool:
    note["updated_at"] = datetime.now(timezone.utc)
    result = await db.doctor_notes.update_one(
        {"_id": note_id},
        {"$set": note}
    )
    return result.modified_count > 0

async def delete_doctor_note(db: AsyncIOMotorDatabase, note_id: str) -> bool:
    result = await db.doctor_notes.delete_one({"_id": note_id})
    return result.deleted_count > 0

# 诊断详情 CRUD 操作
async def create_diagnosis_detail(db: AsyncIOMotorDatabase, detail: MongoDiagnosisDetail) -> str:
    result = await db.diagnosis_details.insert_one(detail.model_dump())
    return str(result.inserted_id)

async def get_diagnosis_detail(db: AsyncIOMotorDatabase, diagnosis_id: int) -> Optional[Dict[str, Any]]:
    return await db.diagnosis_details.find_one({"diagnosis_id": diagnosis_id})

async def update_diagnosis_detail(db: AsyncIOMotorDatabase, diagnosis_id: int, detail: Dict[str, Any]) -> bool:
    detail["updated_at"] = datetime.now(timezone.utc)
    result = await db.diagnosis_details.update_one(
        {"diagnosis_id": diagnosis_id},
        {"$set": detail}
    )
    return result.modified_count > 0

async def delete_diagnosis_detail(db: AsyncIOMotorDatabase, diagnosis_id: int) -> bool:
    result = await db.diagnosis_details.delete_one({"diagnosis_id": diagnosis_id})
    return result.deleted_count > 0 