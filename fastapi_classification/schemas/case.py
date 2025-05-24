from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from ..models.case import CaseStatus

class CaseBase(BaseModel):
    """病例基础模型"""
    id_number: str = Field(..., description="患者身份证号")
    patient_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    status: CaseStatus = CaseStatus.PENDING

class CaseCreate(CaseBase):
    """创建病例请求模型"""
    pass

class CaseUpdate(BaseModel):
    """更新病例请求模型"""
    patient_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    status: Optional[CaseStatus] = None

class CaseResponse(CaseBase):
    """病例响应模型"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)