from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base
import enum

class DiagnosisStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

class DiagnosisPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    
    # 诊断信息
    diagnosis_type = Column(String(50), comment="诊断类型")
    diagnosis_result = Column(Text, comment="诊断结果")
    confidence_score = Column(Float, comment="诊断置信度")
    symptoms = Column(JSON, comment="症状描述")
    treatment_plan = Column(Text, comment="治疗方案")
    follow_up_notes = Column(Text, comment="随访建议")
    priority = Column(Enum(DiagnosisPriority), default=DiagnosisPriority.MEDIUM, comment="诊断优先级")
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 状态
    status = Column(Enum(DiagnosisStatus), default=DiagnosisStatus.PENDING, comment="诊断状态")
    
    # 关联关系
    case = relationship("Case", back_populates="diagnoses")
    doctor = relationship("User", back_populates="diagnoses")