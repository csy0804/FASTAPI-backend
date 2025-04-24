from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    doctor_id = Column(Integer)  # 你可以后续关联到 User
    comment = Column(String)
    case = relationship("Case", back_populates="diagnoses")