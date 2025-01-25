"""
摄像头业务逻辑
包含以下功能：
1. 添加摄像头
2. 删除摄像头

"""

# 摄像头管理服务
import cv2
import json
from datetime import datetime
from app.models.camera import Camera
from app.models.detection import Detection
from app.utils.yolo_integration import YOLOIntegration
from app import db
from app.services.detection_service import DetectionService

class CameraService:
    @staticmethod
    def validate_camera_data(data):
        """验证摄像头数据的完整性和合法性"""
        required_fields = ['name', 'ip_address', 'port', 'url', 
                         'resolution', 'frame_rate', 'encoding_format']
        
        # 检查必填字段
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
                
        # 验证IP地址格式
        ip_parts = data['ip_address'].split('.')
        if len(ip_parts) != 4 or not all(0 <= int(part) <= 255 for part in ip_parts):
            raise ValueError("Invalid IP address format")
            
        # 验证端口范围
        if not 0 <= data['port'] <= 65535:
            raise ValueError("Invalid port number")
            
        return True



    @staticmethod
    def test_camera_connection(url):
        """测试摄像头连接是否正常"""
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            raise ConnectionError("Failed to connect to camera")
        ret, _ = cap.read()
        cap.release()
        if not ret:
            raise ConnectionError("Failed to read frame from camera")
        return True



    @staticmethod
    def add_camera(data):
        """添加摄像头并建立与detection的关联"""
        try:
            # 验证数据
            CameraService.validate_camera_data(data)
            
            # 测试摄像头连接
            CameraService.test_camera_connection(data['url'])
            
            # 创建摄像头记录
            camera = Camera(
                name=data['name'],
                ip_address=data['ip_address'],
                port=data['port'],
                url=data['url'],
                resolution=data['resolution'],
                frame_rate=data['frame_rate'],
                encoding_format=data['encoding_format'],
                model=data.get('model', 'yolov8n.pt'),  # 默认模型
                tracking_config=data.get('tracking_config', 'deep_sort.yaml'),  # 默认跟踪配置
                status='online'
            )
            
            db.session.add(camera)
            db.session.commit()

            # 创建初始detection记录
            detection = Detection(
                camera_id=camera.id,
                timestamp=datetime.now(),
                video_path=f"streams/{camera.id}/live.mp4"
            )
            
            db.session.add(detection)
            db.session.commit()
            
            # 启动视频流处理
            CameraService.start_video_processing(camera)
            
            return {"success": True, "camera_id": camera.id}
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to add camera: {str(e)}")



    @staticmethod
    def start_video_processing(camera):
        """启动视频流处理"""
        try:
            # 准备detection服务需要的数据
            detection_data = {
                "camera_id": camera.id,
                "stream_url": camera.url,
                "model_path": camera.model,
                "tracking_config": camera.tracking_config,
                "output_path": f"streams/{camera.id}/live.mp4"
            }
            
            # 调用detection服务处理视频流
            result = DetectionService.start_detection(detection_data)
            
            if result["success"]:
                camera.status = 'online'
            else:
                camera.status = 'error'
                
            db.session.commit()
            return result
            
        except Exception as e:
            camera.status = 'error'
            db.session.commit()
            raise Exception(f"Failed to start video processing: {str(e)}")

            

    @staticmethod
    def get_camera_stream(camera_id):
        """获取摄像头的处理后视频流"""
        camera = Camera.query.get_or_404(camera_id)
        detection = Detection.query.filter_by(camera_id=camera_id).first()
        
        if not detection or not detection.video_path:
            raise ValueError("No video stream available")
            
        return {
            "stream_url": f"/streams/{camera_id}/live.mp4",
            "camera_status": camera.status
        }

        

    @staticmethod
    def delete_camera(camera_id):
        """
        删除摄像头逻辑
        """
        camera = Camera.query.get_or_404(camera_id)
        db.session.delete(camera)
        db.session.commit()
