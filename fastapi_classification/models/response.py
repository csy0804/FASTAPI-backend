from pydantic import BaseModel
from typing import List


class PredictionResult(BaseModel):
    predicted_label: str  # 分类标签
    confidence_scores: List[float]  # 每个类别对应的置信度分数
