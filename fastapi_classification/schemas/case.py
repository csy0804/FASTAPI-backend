from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CaseBase(BaseModel):
    id_number: str = Field(..., description="患者身份证号")
    patient_name: str
    age: Optional[int]
    gender: Optional[str]

class CaseCreate(CaseBase):
    pass

class CaseUpdate(CaseBase):
    pass

class CaseOut(CaseBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True