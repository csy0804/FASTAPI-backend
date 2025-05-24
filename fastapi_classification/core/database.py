from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi_classification.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_postgres_db():
    """获取PostgreSQL数据库会话"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

async def get_mongodb():
    """获取MongoDB数据库实例"""
    from fastapi_classification.core.mongodb import mongodb
    return mongodb.db