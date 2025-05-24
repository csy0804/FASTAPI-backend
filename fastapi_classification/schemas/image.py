from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.mongodb_models import ImageType, PrivacyLevel

class ImageBase(BaseModel):
    """图片基础模型"""
    image_type: ImageType
    privacy_level: PrivacyLevel
    case_id: Optional[int] = None
    medical_info_id: Optional[int] = None
    diagnosis_id: Optional[int] = None

class ImageCreate(ImageBase):
    """创建图片请求模型"""
    pass

class ImageResponse(ImageBase):
    """图片响应模型"""
    id: str
    user_id: int
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 