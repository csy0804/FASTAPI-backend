from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SurgeryRecord(BaseModel):
    """手术记录"""
    name: str
    year: int
    hospital: Optional[str] = None
    description: Optional[str] = None

class MedicationRecord(BaseModel):
    """用药记录"""
    name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    dosage: str
    frequency: str
    purpose: Optional[str] = None

class PhysicalExamRecord(BaseModel):
    """体检记录"""
    date: datetime
    type: str
    result: str
    hospital: str
    doctor: str

class MedicalInfoBase(BaseModel):
    """医疗信息基础模型"""
    medical_history: Optional[str] = None
    allergy_history: Optional[str] = None
    family_history: Optional[str] = None
    surgery_history: Optional[List[Dict[str, Any]]] = None
    medication_history: Optional[List[Dict[str, Any]]] = None
    physical_exam_records: Optional[List[Dict[str, Any]]] = None
    is_private: Optional[int] = Field(default=1, ge=0, le=2)

class MedicalInfoCreate(MedicalInfoBase):
    """创建医疗信息请求模型"""
    pass

class MedicalInfoUpdate(MedicalInfoBase):
    """更新医疗信息请求模型"""
    pass

class MedicalInfoResponse(MedicalInfoBase):
    """医疗信息响应模型"""
    id: str = Field(validation_alias="_id")
    user_id: int
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class DoctorNoteBase(BaseModel):
    note_content: str

class DoctorNoteCreate(DoctorNoteBase):
    pass

class DoctorNote(DoctorNoteBase):
    id: int
    medical_info_id: int
    doctor_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MedicalInfo(MedicalInfoBase):
    id: int
    user_id: int
    version: int
    created_at: datetime
    updated_at: datetime
    doctor_notes: Optional[List[DoctorNote]] = None

    model_config = ConfigDict(from_attributes=True) 