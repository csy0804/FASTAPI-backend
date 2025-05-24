from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..models.diagnosis import DiagnosisStatus, DiagnosisPriority

class DiagnosisBase(BaseModel):
    """诊断基础模型"""
    diagnosis_type: str
    diagnosis_result: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    symptoms: Optional[List[Dict[str, Any]]] = None
    treatment_plan: Optional[str] = None
    follow_up_notes: Optional[str] = None
    priority: DiagnosisPriority = DiagnosisPriority.MEDIUM
    status: DiagnosisStatus = DiagnosisStatus.PENDING

class DiagnosisCreate(DiagnosisBase):
    """创建诊断请求模型"""
    pass

class DiagnosisUpdate(BaseModel):
    """更新诊断请求模型"""
    diagnosis_type: Optional[str] = None
    diagnosis_result: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    symptoms: Optional[List[Dict[str, Any]]] = None
    treatment_plan: Optional[str] = None
    follow_up_notes: Optional[str] = None
    priority: Optional[DiagnosisPriority] = None
    status: Optional[DiagnosisStatus] = None

class DiagnosisResponse(DiagnosisBase):
    """诊断响应模型"""
    id: int
    case_id: int
    doctor_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 