from sqlalchemy import Boolean, Column, Integer, String, Enum
from ..core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(100))
    role = Column(String(20), default=UserRole.DOCTOR)
    is_active = Column(Boolean, default=True)
    
    # 医生特有字段
    department = Column(String(100), nullable=True)
    title = Column(String(50), nullable=True)  # 职称
    license_number = Column(String(50), nullable=True)  # 执业证号