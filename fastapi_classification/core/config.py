from typing import List

class Settings:
    # 项目基本设置
    PROJECT_NAME: str = "肺部X光分类辅助医疗系统"
    API_V1_STR: str = "/api/v1"
    
    # PostgreSQL 配置
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "yourpassword"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "medical_system1"
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # MongoDB 配置
    MONGODB_URL: str = "mongodb://root:rootpsw@localhost:27017/medical_system1?authSource=admin"
    MONGODB_DB: str = "medical_system1"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = 123456
    REDIS_CACHE_EXPIRE: int = 3600  # 缓存过期时间（秒）
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

# 创建全局设置实例
settings = Settings()