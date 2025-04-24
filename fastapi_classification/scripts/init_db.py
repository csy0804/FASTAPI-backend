from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from fastapi_classification.core.config import settings
import fastapi_classification.core.security

def init_database():
    engine = create_engine(settings.DATABASE_URL)

    # ---- ① 连接测试 ----
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except (OperationalError, SQLAlchemyError) as err:
        print("❌ 数据库连接初始化失败，错误信息：", err)
        return

    print("✅ 数据库连接正常，开始插入初始数据...")

    # 预设密码加密
    admin_plain_password = "admin123"
    doctor_plain_password = "doctor123"
    admin_hashed_password = fastapi_classification.core.security.get_password_hash(admin_plain_password)
    doctor_hashed_password = fastapi_classification.core.security.get_password_hash(doctor_plain_password)

    with engine.begin() as connection:
        # 插入管理员用户
        connection.execute(text("""
            INSERT INTO users (username, email, hashed_password, full_name, role, is_active)
            VALUES (:username, :email, :hashed_password, :full_name, :role, TRUE)
            ON CONFLICT (username) DO NOTHING
        """), {
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": admin_hashed_password,
            "full_name": "System Admin",
            "role": "admin"
        })

        # 插入医生用户
        connection.execute(text("""
            INSERT INTO users (username, email, hashed_password, full_name, role, is_active, department, title, license_number)
            VALUES (:username, :email, :hashed_password, :full_name, :role, TRUE, :department, :title, :license_number)
            ON CONFLICT (username) DO NOTHING
        """), {
            "username": "doctor1",
            "email": "doctor1@example.com",
            "hashed_password": doctor_hashed_password,
            "full_name": "王医生",
            "role": "doctor",
            "department": "呼吸内科",
            "title": "主治医师",
            "license_number": "DOC123456"
        })

        # 获取doctor1用户id
        result = connection.execute(text("SELECT id FROM users WHERE username = :username"), {"username": "doctor1"})
        doctor_id = result.scalar()

        # 插入样例病例，created_by 关联医生
        connection.execute(text("""
                    INSERT INTO cases (id_number, patient_name, age, gender, created_by, created_at, updated_at)
                    VALUES (:id_number, :patient_name, :age, :gender, :created_by, now(), now())
                    ON CONFLICT (id_number) DO NOTHING
                """), {
            "id_number": "123456789012345678",
            "patient_name": "张三",
            "age": 40,
            "gender": "男",
            "created_by": doctor_id
        })

    print("🎉 初始数据插入完成")

if __name__ == "__main__":
    init_database()