import torch
from torchvision import transforms
from PIL import Image


def preprocess_image(image) -> torch.Tensor:
    """对输入的图像进行预处理"""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # 缩放图像到 224x224
        transforms.ToTensor(),  # 转换为张量
        transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))  # 归一化
    ])
    image = Image.open(image).convert('RGB')  # 确保是RGB格式
    image = transform(image).unsqueeze(0)  # 扩展 batch 维度
    return image
