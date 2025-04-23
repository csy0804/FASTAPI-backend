from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi_classification.services.model_service import ModelService
from fastapi_classification.models.response import PredictionResult

# 定义类别标签
CLASS_LABELS = ["新冠肺炎", "肺不透明", "正常", "病毒性肺炎"]

# 初始化ModelService
model_path = "fastapi_classification/model_pth/best.pth"
model_service = ModelService(model_path=model_path, class_labels=CLASS_LABELS)

# 创建路由
router = APIRouter()


@router.post("/predict/", response_model=PredictionResult)
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="仅支持JPEG或PNG格式图片")
    try:
        label, confidence_scores = model_service.predict(file.file)
        return PredictionResult(predicted_label=label, confidence_scores=confidence_scores)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
