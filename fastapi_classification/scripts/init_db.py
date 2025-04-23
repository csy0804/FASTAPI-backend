from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from fastapi_classification.core.config import settings
import fastapi_classification.core.security

def init_database():
    engine = create_engine(settings.DATABASE_URL)

    # ---- ① 连接测试 ----
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # 轻量查询测试
    except (OperationalError, SQLAlchemyError) as err:
        print("❌ 数据库连接初始化失败，错误信息：", err)
        return

    print("✅ 数据库连接正常，开始初始化表结构...")

    # 预设密码加密
    plain_password = "admin123"  # 你想设定的明文密码
    hashed_password = fastapi_classification.core.security.get_password_hash(plain_password)
    # ---- ② 初始化表与插入数据 ----
    with engine.begin() as connection:  # 自动管理事务
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) UNIQUE,
                username VARCHAR(50) UNIQUE,
                hashed_password VARCHAR(100),
                full_name VARCHAR(100),
                role VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                department VARCHAR(100),
                title VARCHAR(50),
                license_number VARCHAR(50)
            )
        """))
        connection.execute(text("""
                    INSERT INTO users (username, email, hashed_password, full_name, role, is_active)
                    VALUES (:username, :email, :hashed_password, :full_name, :role, TRUE)
                    ON CONFLICT (username) DO NOTHING
                """), {
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": hashed_password,
            "full_name": "System Admin",
            "role": "admin"
        })
    print("🎉 数据库表与初始数据初始化完成")

if __name__ == "__main__":
    init_database()
