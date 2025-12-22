import torch
from ultralytics import YOLO

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device 0:", torch.cuda.get_device_name(0))

# 换成你的模型路径
model = YOLO("app/assets/models/yolo11m.pt")

# 将模型放到可用设备（如果已在 CUDA 会显示 cuda:0）
model.to("cuda" if torch.cuda.is_available() else "cpu")
print("model device:", next(model.model.parameters()).device)

# 若要测试一次推理并确认输出在 GPU：
dummy = torch.zeros(1, 3, 640, 640, device=next(model.model.parameters()).device)
with torch.inference_mode():
    out = model.model(dummy)
print("output device:", out[0].device if isinstance(out, (list, tuple)) else out.device)
