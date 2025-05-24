import logging

logger = logging.getLogger(__name__)

from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from fastapi_classification.core.security import get_current_user
from fastapi_classification.models.user import User, UserRole
from fastapi_classification.schemas.image import ImageResponse
from ...core.database import get_mongodb, get_postgres_db
from ...models.mongodb_models import ImageType, PrivacyLevel
from ...services.oss_service import OSSService, oss_service as oss_service_instance
from ...services.database_service import DatabaseService

# 依赖注入函数，提供 DatabaseService 实例
async def get_database_service(
    postgres_db: Session = Depends(get_postgres_db),
    mongodb_db: AsyncIOMotorDatabase = Depends(get_mongodb),
) -> DatabaseService:
    return DatabaseService(postgres_db, mongodb_db)

router = APIRouter()

@router.post("/upload", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    image_type: ImageType = ImageType.MEDICAL_IMAGE,
    privacy_level: PrivacyLevel = PrivacyLevel.DOCTORS_ONLY,
    case_id: Optional[int] = None,
    medical_info_id: Optional[int] = None,
    diagnosis_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service),
    oss_service: OSSService = Depends(lambda: oss_service_instance)
):
    """上传图片"""
    if image_type in [ImageType.MEDICAL_IMAGE, ImageType.MEDICAL_REPORT] and current_user.role != UserRole.DOCTOR:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有医生可以上传医疗相关图片")

    mongo_image_data = await oss_service.upload_file(
        file=file,
        user_id=current_user.id,
        image_type=image_type,
        privacy_level=privacy_level,
        case_id=case_id,
        medical_info_id=medical_info_id,
        diagnosis_id=diagnosis_id
    )

    created_image = await db_service.create_image(mongo_image_data)

    return ImageResponse.model_validate(created_image)

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: str,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """获取图片信息"""
    image = await db_service.get_image(image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    if image.privacy_level == PrivacyLevel.DOCTORS_ONLY and current_user.role != UserRole.DOCTOR:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此图片")

    return ImageResponse.model_validate(image)

@router.get("/{image_id}/url")
async def get_image_url(
    image_id: str,
    expires: int = 3600,
    db_service: DatabaseService = Depends(get_database_service),
    oss_service: OSSService = Depends(lambda: oss_service_instance),
    current_user: User = Depends(get_current_user)
):
    """获取图片访问URL"""
    image = await db_service.get_image(image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    if image.privacy_level == PrivacyLevel.DOCTORS_ONLY and current_user.role != UserRole.DOCTOR:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此图片")

    url = await oss_service.get_file_url(image, expires)
    return {"url": url}

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: str,
    db_service: DatabaseService = Depends(get_database_service),
    oss_service: OSSService = Depends(lambda: oss_service_instance),
    current_user: User = Depends(get_current_user)
):
    """删除图片"""
    image = await db_service.get_image(image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    if image.user_id != current_user.id and current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此图片")

    await oss_service.delete_file(image)

    delete_success = await db_service.delete_image(image_id)
    if not delete_success:
         logger.error(f"删除图片记录失败: {image_id}")

    return

@router.get("/user/{user_id}", response_model=List[ImageResponse])
async def get_user_images(
    user_id: int,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """获取指定用户的所有图片"""
    if current_user.id != user_id and current_user.role != UserRole.DOCTOR:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看其他用户的图片")

    images = await db_service.get_user_images(user_id)

    return [ImageResponse.model_validate(image) for image in images]

@router.get("/case/{case_id}", response_model=List[ImageResponse])
async def get_case_images(
    case_id: int,
    db_service: DatabaseService = Depends(get_database_service),
    current_user: User = Depends(get_current_user)
):
    """获取病例相关的所有图片"""
    images = await db_service.get_case_images(case_id)
    return [ImageResponse.model_validate(image) for image in images] 