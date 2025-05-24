import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
import oss2
from fastapi import UploadFile, HTTPException
from ..core.oss_config import OSSConfig
from ..models.mongodb_models import MongoImage, ImageType, PrivacyLevel

logger = logging.getLogger(__name__)

class OSSService:
    def __init__(self, config: OSSConfig):
        self.config = config
        self.auth = oss2.Auth(config.access_key_id, config.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, config.endpoint, config.bucket_name)

    async def upload_file(
        self,
        file: UploadFile,
        user_id: int,
        image_type: ImageType,
        privacy_level: PrivacyLevel = PrivacyLevel.DOCTORS_ONLY,
        case_id: Optional[int] = None,
        medical_info_id: Optional[int] = None,
        diagnosis_id: Optional[int] = None
    ) -> MongoImage:
        """上传文件到OSS并创建图片记录"""
        # 验证文件类型
        if file.content_type not in self.config.allowed_types:
            raise HTTPException(status_code=400, detail="不支持的文件类型")

        # 验证文件大小
        file_size = 0
        file_content = b""
        while chunk := await file.read(8192):
            file_size += len(chunk)
            file_content += chunk
            if file_size > self.config.max_size:
                raise HTTPException(status_code=400, detail="文件大小超过限制")

        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        object_key = f"{self.config.upload_dir}/{datetime.now().strftime('%Y/%m/%d')}/{unique_filename}"

        try:
            # 上传到OSS
            self.bucket.put_object(object_key, file_content)
            
            # 获取文件URL
            file_url = f"{self.config.base_url}/{object_key}"

            # 创建图片记录
            image = MongoImage(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=object_key,
                file_url=file_url,
                file_size=file_size,
                mime_type=file.content_type,
                image_type=image_type,
                user_id=user_id,
                case_id=case_id,
                medical_info_id=medical_info_id,
                diagnosis_id=diagnosis_id,
                privacy_level=privacy_level,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )

            return image

        except Exception as e:
            # 如果上传失败，尝试删除已上传的文件
            try:
                self.bucket.delete_object(object_key)
            except:
                pass
            logger.error(f"文件上传失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

    async def delete_file(self, image: MongoImage) -> bool:
        """删除OSS中的文件"""
        try:
            self.bucket.delete_object(image.file_path)
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

    async def get_file_url(self, image: MongoImage, expires: int = 3600) -> str:
        """获取文件的临时访问URL"""
        try:
            url = self.bucket.sign_url('GET', image.file_path, expires)
            return url
        except Exception as e:
            logger.error(f"获取文件URL失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取文件URL失败: {str(e)}")

    async def update_file_privacy(self, image: MongoImage, privacy_level: PrivacyLevel) -> bool:
        """更新文件的隐私设置"""
        try:
            # 这里可以添加OSS的访问控制策略更新
            # 例如：设置文件的ACL或更新Bucket Policy
            image.privacy_level = privacy_level
            image.updated_at = datetime.now(timezone.utc)
            return True
        except Exception as e:
            logger.error(f"更新文件隐私设置失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"更新文件隐私设置失败: {str(e)}")

    async def get_file_info(self, image: MongoImage) -> dict:
        """获取文件信息"""
        try:
            # 获取文件元数据
            headers = self.bucket.head_object(image.file_path)
            return {
                "size": headers.content_length,
                "last_modified": headers.last_modified,
                "etag": headers.etag,
                "content_type": headers.content_type
            }
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")

oss_service = OSSService(OSSConfig()) 