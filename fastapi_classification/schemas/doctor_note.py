from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from .medical_info import MedicalInfoResponse

class NoteType(str, Enum):
    """笔记类型枚举"""
    OBSERVATION = "observation"  # 观察记录
    DIAGNOSIS = "diagnosis"      # 诊断记录
    TREATMENT = "treatment"      # 治疗记录
    FOLLOW_UP = "follow_up"      # 随访记录
    OTHER = "other"             # 其他记录

class DoctorNoteBase(BaseModel):
    """医生笔记基础模型"""
    note_content: str = Field(
        ...,
        description="笔记内容",
        example="患者今日体温37.2℃，精神状态良好。主诉：轻微头痛，无其他不适。查体：血压120/80mmHg，心率75次/分，呼吸18次/分。建议：继续服用布洛芬，每日三次，每次0.3g；多休息，保持充足睡眠；3天后复诊。"
    )
    medical_info_id: int = Field(
        ...,
        description="医疗信息ID",
        example=1,
        gt=0
    )
    note_type: NoteType = Field(
        ...,
        description="笔记类型",
        example=NoteType.OBSERVATION
    )

    class Config:
        json_schema_extra = {
            "example": {
                "note_content": "患者今日体温37.2℃，精神状态良好。主诉：轻微头痛，无其他不适。查体：血压120/80mmHg，心率75次/分，呼吸18次/分。建议：继续服用布洛芬，每日三次，每次0.3g；多休息，保持充足睡眠；3天后复诊。",
                "medical_info_id": 1,
                "note_type": "observation"
            }
        }

class DoctorNoteCreate(DoctorNoteBase):
    """创建医生笔记请求模型"""
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "观察记录",
                    "description": "记录患者的基本观察情况",
                    "value": {
                        "note_content": "患者今日体温37.2℃，精神状态良好。主诉：轻微头痛，无其他不适。查体：血压120/80mmHg，心率75次/分，呼吸18次/分。建议：继续服用布洛芬，每日三次，每次0.3g；多休息，保持充足睡眠；3天后复诊。",
                        "medical_info_id": 1,
                        "note_type": "observation"
                    }
                },
                {
                    "summary": "诊断记录",
                    "description": "记录医生的诊断结果",
                    "value": {
                        "note_content": "初步诊断：上呼吸道感染。依据：1. 患者主诉咽痛、咳嗽3天；2. 查体：咽部充血，扁桃体I度肿大；3. 体温37.5℃，血常规示白细胞计数12.5×10^9/L。建议：1. 口服阿莫西林胶囊0.5g，每日三次；2. 布洛芬片0.3g，必要时服用；3. 多饮水，注意休息；4. 3天后复诊。",
                        "medical_info_id": 1,
                        "note_type": "diagnosis"
                    }
                },
                {
                    "summary": "治疗记录",
                    "description": "记录治疗方案和执行情况",
                    "value": {
                        "note_content": "治疗方案：1. 已开具阿莫西林胶囊0.5g×24粒，用法：0.5g，每日三次，饭后服用；2. 布洛芬片0.3g×10片，用法：0.3g，必要时服用；3. 已进行雾化吸入治疗，使用布地奈德混悬液2mg，每日两次。患者已理解用药方法，无不良反应。",
                        "medical_info_id": 1,
                        "note_type": "treatment"
                    }
                },
                {
                    "summary": "随访记录",
                    "description": "记录患者随访情况",
                    "value": {
                        "note_content": "随访情况：患者服药3天后复诊，主诉症状明显改善。查体：咽部充血减轻，扁桃体恢复正常大小，体温36.8℃。血常规复查：白细胞计数8.5×10^9/L。建议：1. 继续服用阿莫西林胶囊3天；2. 停用布洛芬；3. 继续雾化吸入治疗2天；4. 1周后复查。",
                        "medical_info_id": 1,
                        "note_type": "follow_up"
                    }
                }
            ]
        }

class DoctorNoteUpdate(BaseModel):
    """更新医生笔记请求模型"""
    note_content: Optional[str] = Field(
        None,
        description="笔记内容",
        example="患者今日体温36.8℃，精神状态良好。主诉：头痛症状明显改善。查体：血压118/78mmHg，心率72次/分，呼吸16次/分。建议：继续服用布洛芬，每日两次，每次0.3g；适当活动，避免剧烈运动；2天后复诊。"
    )
    note_type: Optional[NoteType] = Field(
        None,
        description="笔记类型",
        example=NoteType.FOLLOW_UP
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "更新笔记内容",
                    "description": "更新笔记的具体内容",
                    "value": {
                        "note_content": "患者今日体温36.8℃，精神状态良好。主诉：头痛症状明显改善。查体：血压118/78mmHg，心率72次/分，呼吸16次/分。建议：继续服用布洛芬，每日两次，每次0.3g；适当活动，避免剧烈运动；2天后复诊。"
                    }
                },
                {
                    "summary": "更新笔记类型",
                    "description": "将笔记类型更改为随访记录",
                    "value": {
                        "note_type": "follow_up"
                    }
                },
                {
                    "summary": "同时更新内容和类型",
                    "description": "更新笔记内容和类型",
                    "value": {
                        "note_content": "患者今日体温36.8℃，精神状态良好。主诉：头痛症状明显改善。查体：血压118/78mmHg，心率72次/分，呼吸16次/分。建议：继续服用布洛芬，每日两次，每次0.3g；适当活动，避免剧烈运动；2天后复诊。",
                        "note_type": "follow_up"
                    }
                }
            ]
        }

class DoctorNoteResponse(DoctorNoteBase):
    """医生笔记响应模型"""
    id: int = Field(..., description="笔记ID", example=1)
    doctor_id: int = Field(..., description="医生ID", example=1)
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    medical_info: Optional[MedicalInfoResponse] = Field(None, description="关联的医疗信息")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "doctor_id": 1,
                "note_content": "患者今日体温37.2℃，精神状态良好。主诉：轻微头痛，无其他不适。查体：血压120/80mmHg，心率75次/分，呼吸18次/分。建议：继续服用布洛芬，每日三次，每次0.3g；多休息，保持充足睡眠；3天后复诊。",
                "medical_info_id": 1,
                "note_type": "observation",
                "created_at": "2024-03-20T10:00:00Z",
                "updated_at": "2024-03-20T10:00:00Z",
                "medical_info": {
                    "_id": "65f9a1b2c3d4e5f6g7h8i9j0",
                    "user_id": 1,
                    "medical_history": "高血压病史5年，规律服用降压药。",
                    "allergy_history": "对青霉素过敏。",
                    "family_history": "父亲有高血压病史。",
                    "surgery_history": [
                        {
                            "name": "阑尾切除术",
                            "year": 2010,
                            "hospital": "市第一人民医院",
                            "description": "急性阑尾炎"
                        }
                    ],
                    "medication_history": [
                        {
                            "name": "复方降压片",
                            "start_date": "2023-01-01T00:00:00Z",
                            "end_date": None,
                            "dosage": "1片",
                            "frequency": "每日一次",
                            "purpose": "控制血压"
                        }
                    ],
                    "physical_exam_records": [
                        {
                            "date": "2024-03-15T09:00:00Z",
                            "type": "常规体检",
                            "result": "血压偏高，其他指标正常。",
                            "hospital": "市第一人民医院",
                            "doctor": "张医生"
                        }
                    ],
                    "version": 1,
                    "created_at": "2024-03-15T08:00:00Z",
                    "updated_at": "2024-03-15T08:00:00Z"
                }
            }
        } 