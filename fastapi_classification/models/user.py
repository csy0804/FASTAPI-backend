from sqlalchemy import Boolean, Column, Integer, String, Enum, Text
from ..core.database import Base
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)
    
    # 医生特有字段
    department = Column(String(100), nullable=True)
    title = Column(String(50), nullable=True)  # 职称
    license_number = Column(String(50), nullable=True)  # 执业证号

    # 关联关系
    cases = relationship("Case", back_populates="creator")
    diagnoses = relationship("Diagnosis", back_populates="doctor")
    doctor_notes = relationship("DoctorNote", back_populates="doctor")
    medical_info = relationship("MedicalInfo", back_populates="user", uselist=False, cascade="all, delete-orphan")

    @hybrid_property
    def is_doctor(self) -> bool:
        """判断用户是否为医生"""
        return self.role == UserRole.DOCTOR

    @hybrid_property
    def is_admin(self) -> bool:
        """判断用户是否为管理员"""
        return self.role == UserRole.ADMIN

    @hybrid_property
    def is_patient(self) -> bool:
        """判断用户是否为患者"""
        return self.role == UserRole.PATIENT

'''# 患者表
class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    phone = Column(String(15))
    medical_history = Column(Text)
    allergies = Column(Text)'''