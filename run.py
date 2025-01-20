import torch
from ultralytics import YOLO

# 假设 model 是你的 YOLOv11 或 BoT-SORT 模型
model = YOLO("yolo11m.pt")

# 检查模型是否在 GPU 上
if next(model.parameters()).is_cuda:
    print("模型在 GPU 上运行")
else:
    print("模型在 CPU 上运行")