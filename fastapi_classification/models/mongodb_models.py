from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from .medical_info import MedicalInfo, PrivacyLevel
from .doctor_note import DoctorNote, NoteType
from .diagnosis import Diagnosis, DiagnosisStatus, DiagnosisPriority
from bson import ObjectId

class PrivacyLevel(str, Enum):
    PUBLIC = "public"  # 公开
    DOCTORS_ONLY = "doctors_only"  # 仅医生可见
    PRIVATE = "private"  # 完全私密

class NoteType(str, Enum):
    OBSERVATION = "observation"  # 观察记录
    TREATMENT = "treatment"  # 治疗记录
    FOLLOW_UP = "follow_up"  # 随访记录
    REFERRAL = "referral"  # 转诊记录
    OTHER = "other"  # 其他

class DiagnosisStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

class DiagnosisPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ImageType(str, Enum):
    MEDICAL_IMAGE = "medical_image"  # 医学影像
    DOCUMENT = "document"  # 文档扫描
    PHOTO = "photo"  # 照片
    OTHER = "other"  # 其他

class MongoImage(BaseModel):
    """MongoDB图片模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    filename: str  # 文件名
    original_filename: str  # 原始文件名
    file_path: str  # 文件在存储服务中的路径
    file_url: str  # 文件访问URL
    file_size: int  # 文件大小（字节）
    mime_type: str  # 文件MIME类型
    image_type: ImageType  # 图片类型
    width: Optional[int] = None  # 图片宽度
    height: Optional[int] = None  # 图片高度
    format: Optional[str] = None  # 图片格式
    image_metadata: Dict[str, Any] = {}  # 图片元数据
    tags: List[str] = []  # 标签
    user_id: int  # 上传用户ID
    case_id: Optional[int] = None  # 关联的病例ID
    medical_info_id: Optional[int] = None  # 关联的医疗信息ID
    diagnosis_id: Optional[int] = None  # 关联的诊断ID
    privacy_level: PrivacyLevel = PrivacyLevel.DOCTORS_ONLY  # 隐私级别
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = False  # 是否已删除

class MongoMedicalInfo(BaseModel):
    """MongoDB医疗信息模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: int
    case_id: Optional[int] = None
    medical_history: str = ""
    allergy_history: str = ""
    family_history: str = ""
    surgery_history: List[Dict[str, Any]] = []
    medication_history: List[Dict[str, Any]] = []
    physical_exam_records: List[Dict[str, Any]] = []
    privacy_level: PrivacyLevel = PrivacyLevel.DOCTORS_ONLY
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_reviewed_at: Optional[datetime] = None
    version: int = 1

class MongoDoctorNote(BaseModel):
    """MongoDB医生笔记模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    doctor_id: int
    medical_info_id: int
    note_type: NoteType = NoteType.OBSERVATION
    note_content: str
    is_important: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MongoDiagnosisDetail(BaseModel):
    """MongoDB诊断详情模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    diagnosis_id: int  # 关联到PostgreSQL的Diagnosis表
    symptoms: Dict[str, Any] = {}  # 症状详情
    treatment_plan: str = ""  # 详细治疗方案
    follow_up_notes: str = ""  # 随访记录
    analysis: Dict[str, Any] = {  # 分析数据
        "confidence_score": 0.0,
        "supporting_evidence": []
    }
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 