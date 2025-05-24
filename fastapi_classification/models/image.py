from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    
    # 文件信息
    file_path = Column(String, nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, comment="文件大小（字节）")
    
    # 图像元数据
    width = Column(Integer, comment="图像宽度")
    height = Column(Integer, comment="图像高度")
    format = Column(String(10), comment="图像格式")
    image_metadata = Column(JSON, comment="其他元数据")
    
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
    case = relationship("Case", back_populates="images")
