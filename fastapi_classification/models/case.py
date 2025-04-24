from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from ..core.database import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    id_number = Column(String(32), nullable=False, unique=True, index=True, comment="患者身份证号")
    patient_name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
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

    creator = relationship("User", back_populates="cases")
    # 如果你还没有Image和Diagnosis模型，可以先注释掉下面两行
    images = relationship("Image", back_populates="case", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="case", cascade="all, delete-orphan")