from pydantic import BaseModel

class OSSConfig(BaseModel):
    """阿里云OSS配置"""
    access_key_id: str = "your_access_key_id"
    access_key_secret: str = "your_access_key_secret"
    endpoint: str = "oss-cn-hangzhou.aliyuncs.com"  # 根据您的地区修改
    bucket_name: str = "your-bucket-name"
    base_url: str = "https://your-bucket-name.oss-cn-hangzhou.aliyuncs.com"  # 访问域名
    max_size: int = 10 * 1024 * 1024  # 最大文件大小（10MB）
    allowed_types: list = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    upload_dir: str = "medical_images"  # 上传目录 