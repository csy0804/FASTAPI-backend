import torch
from fastapi_classification.services.image_utils import preprocess_image


class ModelService:
    def __init__(self, model_path: str, class_labels: list):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_labels = class_labels
        self.model = self._load_model(model_path)  # 加载模型


    def _load_model(self, model_path: str):
        """加载用于推理的深度学习模型"""
        from ..model.cnn import simplecnn  # 确保可以导入您的模型定义
        model = simplecnn(num_class=len(self.class_labels))
        model.load_state_dict(torch.load(model_path, map_location=self.device), strict=True)
        model.to(self.device).eval()  # 设置为评估模式
        return model

    def predict(self, image_path: str):
        """对图像进行分类"""
        input_tensor = preprocess_image(image_path).to(self.device)
        with torch.no_grad():  # 禁用梯度计算
            output = self.model(input_tensor)  # 得到推理结果
            predicted_index = torch.argmax(output, dim=1).item()  # 获取预测类别索引
            confidence_scores = output.softmax(dim=1)[0].tolist()  # 获取每个类别的置信度
        return self.class_labels[predicted_index], confidence_scores
