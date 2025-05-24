from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base
import enum

class NoteType(str, enum.Enum):
    OBSERVATION = "observation"  # 观察记录
    TREATMENT = "treatment"  # 治疗记录
    FOLLOW_UP = "follow_up"  # 随访记录
    REFERRAL = "referral"  # 转诊记录
    OTHER = "other"  # 其他

class DoctorNote(Base):
    __tablename__ = 'doctor_notes'

    id = Column(Integer, primary_key=True, index=True)
    medical_info_id = Column(Integer, ForeignKey('medical_info.id'))
    doctor_id = Column(Integer, ForeignKey('users.id'))
    case_id = Column(Integer, ForeignKey('cases.id'))
    
    # 笔记内容
    note_type = Column(Enum(NoteType), default=NoteType.OBSERVATION, comment="笔记类型")
    note_content = Column(Text, nullable=False)
    is_important = Column(Boolean, default=False, comment="是否重要笔记")
    
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
    medical_info = relationship("MedicalInfo", back_populates="doctor_notes")
    doctor = relationship("User", back_populates="doctor_notes")
    case = relationship("Case", back_populates="doctor_notes") 