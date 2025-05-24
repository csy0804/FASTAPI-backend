import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_classification.core.config import settings
from fastapi_classification.core.database import Base
from fastapi_classification.core.mongodb import mongodb
from fastapi_classification.services.sync_service import SyncService
from contextlib import contextmanager

# 导入模型和密码哈希函数
from fastapi_classification.models.user import User, UserRole
from fastapi_classification.models.case import Case, CaseStatus
from fastapi_classification.models.medical_info import MedicalInfo, PrivacyLevel
from fastapi_classification.models.diagnosis import Diagnosis, DiagnosisStatus, DiagnosisPriority
from fastapi_classification.models.doctor_note import DoctorNote, NoteType
from fastapi_classification.models.image import Image # 导入 Image 模型
from fastapi_classification.core.security import get_password_hash
from datetime import datetime, timezone
import json

@contextmanager
def get_db_session():
    """创建数据库会话的上下文管理器"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_postgres():
    """初始化 PostgreSQL 数据库"""
    engine = create_engine(settings.DATABASE_URL)
    # 添加这一行来删除现有表
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with get_db_session() as db:
        try:
            # 这里可以添加初始数据
            print("正在添加初始数据...")

            # 添加示例用户
            admin_user = db.query(User).filter(User.email == "admin@example.com").first()
            if not admin_user:
                print("创建管理员用户...")
                admin_user = User(
                    email="admin@example.com",
                    username="admin",
                    hashed_password=get_password_hash("admin_password_secure"), # <-- 替换为安全的密码
                    full_name="Admin User",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                db.add(admin_user)
                # 不需要在这里 commit，稍后一起 commit

            doctor_user = db.query(User).filter(User.email == "doctor@example.com").first()
            if not doctor_user:
                print("创建医生用户...")
                doctor_user = User(
                    email="doctor@example.com",
                    username="doctor",
                    hashed_password=get_password_hash("doctor_password_secure"), # <-- 替换为安全的密码
                    full_name="Dr. Smith",
                    role=UserRole.DOCTOR,
                    is_active=True,
                    department="Cardiology",
                    title="Senior Cardiologist",
                    license_number="D12345"
                )
                db.add(doctor_user)

            patient_user = db.query(User).filter(User.email == "patient@example.com").first()
            if not patient_user:
                print("创建患者用户...")
                patient_user = User(
                    email="patient@example.com",
                    username="patient",
                    hashed_password=get_password_hash("patient_password_secure"), # <-- 替换为安全的密码
                    full_name="Patient Zero",
                    role=UserRole.PATIENT,
                    is_active=True,
                )
                db.add(patient_user)

            # 提交用户并刷新以获取 ID
            db.commit()
            db.refresh(admin_user)
            db.refresh(doctor_user)
            db.refresh(patient_user)
            print("示例用户创建成功！")

            # 添加示例病例
            example_case = db.query(Case).filter(Case.id_number == "11010120000101123X").first()
            if not example_case:
                 print("创建示例病例...")
                 example_case = Case(
                     id_number="11010120000101123X", # 示例身份证号
                     patient_name="患者零号",
                     age=30,
                     gender="Male",
                     created_by=admin_user.id, # 由管理员创建
                     status=CaseStatus.PENDING
                 )
                 db.add(example_case)
                 db.commit()
                 db.refresh(example_case)
                 print("示例病例创建成功！")

            # 添加示例医疗信息 (关联患者用户)
            example_medical_info = db.query(MedicalInfo).filter(MedicalInfo.user_id == patient_user.id).first()
            if not example_medical_info:
                print("创建示例医疗信息...")
                example_medical_info = MedicalInfo(
                    user_id=patient_user.id,
                    medical_history="患有慢性咳嗽多年。",
                    allergy_history="无已知过敏史。",
                    family_history="父亲有高血压。",
                    surgery_history=json.dumps([{"name": "阑尾切除术", "year": 2010}]), # 示例 JSON 数据
                    medication_history=json.dumps([{"name": "复方甘草片", "dosage": "每日三次", "duration": "一月"}]),
                    physical_exam_records=json.dumps([{"date": "2023-01-15", "summary": "体温正常，听诊有少量干啰音。"}]),
                    privacy_level=PrivacyLevel.DOCTORS_ONLY
                )
                db.add(example_medical_info)
                db.commit()
                db.refresh(example_medical_info)
                print("示例医疗信息创建成功！")

            # 添加示例诊断 (关联病例和医生)
            example_diagnosis = db.query(Diagnosis).filter(Diagnosis.case_id == example_case.id).first()
            if not example_diagnosis:
                print("创建示例诊断...")
                example_diagnosis = Diagnosis(
                    case_id=example_case.id,
                    doctor_id=doctor_user.id,
                    diagnosis_result="初步诊断为支气管炎",
                    diagnosis_type="初步诊断",
                    status=DiagnosisStatus.PENDING,
                    priority=DiagnosisPriority.MEDIUM
                )
                db.add(example_diagnosis)
                db.commit()
                db.refresh(example_diagnosis)
                print("示例诊断创建成功！")

            # 添加示例医生笔记 (关联医疗信息、病例和医生)
            example_doctor_note = db.query(DoctorNote).filter(DoctorNote.medical_info_id == example_medical_info.id).first()
            if not example_doctor_note:
                print("创建示例医生笔记...")
                example_doctor_note = DoctorNote(
                    medical_info_id=example_medical_info.id,
                    doctor_id=doctor_user.id,
                    case_id=example_case.id, # 也关联病例
                    note_type=NoteType.OBSERVATION,
                    note_content="患者今日复查，咳嗽有所减轻，建议继续用药。",
                    is_important=False
                )
                db.add(example_doctor_note)
                db.commit()
                db.refresh(example_doctor_note)
                print("示例医生笔记创建成功！")

            # 添加示例图片 (关联病例和上传用户)
            example_image = db.query(Image).filter(Image.case_id == example_case.id).first()
            if not example_image:
                 print("创建示例图片记录...")
                 example_image = Image(
                     case_id=example_case.id,
                     file_path="uploads/example/example.jpg", # 示例文件路径
                     file_name="example.jpg",
                     file_type="image/jpeg",
                     file_size=102400, # 示例文件大小
                     width=800,
                     height=600,
                     format="jpeg",
                     image_metadata=json.dumps({"scanner": "XrayScan 1.0"}), # 示例元数据
                     created_at=datetime.now(timezone.utc),
                     updated_at=datetime.now(timezone.utc),
                 )
                 db.add(example_image)
                 db.commit()
                 print("示例图片记录创建成功！")


            print("初始数据添加完成。")

            return db
        except Exception as e:
            db.rollback() # 如果出错，回滚事务
            print(f"初始化 PostgreSQL 数据库时发生错误: {str(e)}")
            raise

async def init_mongodb():
    """初始化 MongoDB 数据库"""
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB]

        # 确保集合存在（如果不存在，创建索引也会创建集合）
        # await db.medical_info.create_index("user_id", unique=True)
        # await db.diagnosis_details.create_index("diagnosis_id", unique=True)
        # await db.doctor_notes.create_index([("medical_info_id", 1), ("created_at", -1)])

        # 已经修改为由 SyncService 处理索引创建和数据同步

        return db
    except Exception as e:
        print(f"初始化 MongoDB 数据库时发生错误: {str(e)}")
        raise

async def init_databases():
    """初始化所有数据库并同步数据"""
    try:
        print("初始化 PostgreSQL 数据库...")
        # init_postgres 现在负责创建表和插入初始数据
        postgres_db_session = await init_postgres()
        print("PostgreSQL 数据库初始化完成！")

        print("初始化 MongoDB 数据库...")
        # 直接获取数据库实例
        mongo_db = await init_mongodb()
        print("MongoDB 数据库初始化完成！")

        print("开始同步数据...")
        # 将 SQLAlchemy Session 传递给 SyncService，以及 MongoDB 数据库对象
        sync_service = SyncService(postgres_db_session, mongo_db)
        await sync_service.sync_all_data()
        print("数据同步完成！")
    except Exception as e:
        # 在这里捕获 init_databases 中的异常并打印详细信息
        print(f"初始化数据库时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(init_databases())