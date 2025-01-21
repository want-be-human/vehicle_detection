"""
应用启动时加载摄像头并启动实时检测任务
"""

from flask import Flask
from app.config import Config
from app.models.camera import Camera
from app.services.detection_service import DetectionService
from app.utils.logging_utils import log_info

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
from app import db
db.init_app(app)

# 启动实时检测任务
with app.app_context():
    detection_service = DetectionService()
    cameras = Camera.query.filter_by(is_active=True).all()
    for camera in cameras:
        log_info(f"Starting detection for camera: {camera.name}")
        detection_service.start_realtime_detection(camera.id)
