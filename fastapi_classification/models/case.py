from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base
import enum

class CaseStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    id_number = Column(String(32), nullable=False, unique=True, index=True, comment="患者身份证号")
    patient_name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # 状态管理
    status = Column(Enum(CaseStatus), default=CaseStatus.PENDING, comment="病例状态")
    
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

    # 关联关系
    creator = relationship("User", back_populates="cases")
    diagnoses = relationship("Diagnosis", back_populates="case", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="case", cascade="all, delete-orphan")
    doctor_notes = relationship("DoctorNote", back_populates="case", cascade="all, delete-orphan")