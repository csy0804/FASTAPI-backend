from typing import List
from pydantic import BaseModel

class Settings(BaseModel):
    # 项目基本设置
    PROJECT_NAME: str = "肺部X光分类辅助医疗系统"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql+psycopg2://postgres:yourpassword@localhost:5432/medical_system1"

    # JWT配置
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True

# 创建全局设置实例
settings = Settings()