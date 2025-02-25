from datetime import datetime
import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from app import db, create_app
from app.models.camera import Camera
from app.models.detection import Detection
from app.models.statistics import StatisticsModel
from app.config import Config

def init_db():
    """初始化数据库"""
    app = create_app(Config)
    with app.app_context():
        # 删除所有表并重新创建
        db.drop_all()
        db.create_all()
        
        # 添加测试摄像头
        test_cameras = [
            Camera(
                name='Camera 1',
                ip_address='192.168.1.100',
                port=554,
                url='rtsp://192.168.1.100:554/stream1',
                resolution='1920x1080',
                frame_rate=30,
                encoding_format='H.264',
                model='yolov8n.pt',
                tracking_config='deep_sort.yaml'
            ),
            Camera(
                name='Camera 2',
                ip_address='192.168.1.101',
                port=554,
                url='rtsp://192.168.1.101:554/stream1',
                resolution='1920x1080',
                frame_rate=30,
                encoding_format='H.264',
                model='yolov8n.pt',
                tracking_config='deep_sort.yaml'
            )
        ]
        db.session.add_all(test_cameras)
        
        # 添加测试检测记录
        test_detections = [
            Detection(
                camera_id=1,
                timestamp=datetime.now(),
                vehicle_type='truck',
                location='Gate 1',
                video_path='/videos/detection_1.mp4',
                is_violation=False
            ),
            Detection(
                camera_id=1,
                timestamp=datetime.now(),
                video_path='/videos/record_1.mp4'
            )
        ]
        db.session.add_all(test_detections)
        
        # 添加测试统计数据
        test_statistics = StatisticsModel(
            date=datetime.now().date(),  # 使用 date 字段
            vehicle_distribution={'car': 100, 'bus': 50},  # 使用正确的字段名
            hourly_flow=[{"hour": 0, "count": 30}],
            total_count=150,
            chart_data={"peak_chart": {}, "distribution_chart": {}}
        )
        db.session.add(test_statistics)
        
        # 提交所有更改
        db.session.commit()
        
        print("数据库初始化完成。")

if __name__ == '__main__':
    init_db()
