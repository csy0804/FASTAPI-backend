from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base
import enum

class PrivacyLevel(str, enum.Enum):
    PUBLIC = "public"  # 公开
    DOCTORS_ONLY = "doctors_only"  # 仅医生可见
    PRIVATE = "private"  # 完全私密

class MedicalInfo(Base):
    __tablename__ = 'medical_info'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # 基本信息
    medical_history = Column(Text, comment="病史")
    allergy_history = Column(Text, comment="过敏史")
    family_history = Column(Text, comment="家族病史")
    
    # 手术历史
    surgery_history = Column(JSON, comment="手术历史")
    
    # 用药历史
    medication_history = Column(JSON, comment="用药历史")
    
    # 体检记录
    physical_exam_records = Column(JSON, comment="体检记录")
    
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
    last_reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后审核时间"
    )
    
    # 版本控制
    version = Column(Integer, default=1, comment="版本号")
    
    # 隐私设置
    privacy_level = Column(
        Enum(PrivacyLevel),
        default=PrivacyLevel.DOCTORS_ONLY,
        comment="隐私级别"
    )
    
    # 关联关系
    user = relationship("User", back_populates="medical_info")
    doctor_notes = relationship("DoctorNote", back_populates="medical_info", cascade="all, delete-orphan")