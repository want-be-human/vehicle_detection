"""
摄像头管理服务 (CameraService)

主要功能：
1. 摄像头管理：
   - 添加新摄像头
   - 删除现有摄像头 
   - 更新摄像头配置
   - 管理禁停区域

2. 视频流处理：
   - 验证摄像头连接
   - 启动视频流处理
   - 获取处理后的视频流

与前端交互：
1. 通过 camera_blueprint 路由接口:
   - POST /camera/cameras: 添加新摄像头
   - DELETE /camera/cameras/<id>: 删除摄像头
   - PUT /camera/cameras/<id>/restricted-areas: 更新禁停区域

2. WebSocket 实时通信:
   - 通过 socketio 推送视频流
   - 实时更新摄像头状态
   - 发送违规检测结果

数据流向：
Frontend -> REST API -> CameraService -> Database
                   -> WebSocket -> Frontend (实时数据)

工作流程：
1. 添加摄像头:
   Frontend POST /camera/cameras 
   -> CameraService.add_camera()
   -> 验证数据
   -> 测试连接
   -> 创建数据库记录
   -> 启动视频处理
   -> 返回结果给前端

2. 视频处理:
   CameraService.start_video_processing()
   -> DetectionService.start_detection()
   -> YOLOIntegration 处理
   -> WebSocket 推送结果
   -> 前端展示

3. 禁停区域管理:
   Frontend PUT /camera/restricted-areas
   -> CameraService.update_restricted_areas()
   -> 更新数据库
   -> 实时生效于检测逻辑

异常处理：
- 数据验证异常
- 连接测试异常
- 视频处理异常
- 数据库操作异常

关联服务：
- DetectionService: 视频检测服务
- ViolationService: 违规检测服务
- StatisticsService: 统计服务

数据模型：
- Camera: 摄像头信息模型
- Detection: 检测记录模型

配置管理：
- 默认模型：yolov8n.pt
- 默认跟踪器：botsort.yaml
- 视频存储路径：streams/<camera_id>/

性能考虑：
- 使用数据库事务确保数据一致性
- 异步处理视频流
- 文件系统操作异常处理
"""

# 摄像头管理服务
import cv2
import os
from datetime import datetime
from app.models.camera import Camera
from app.models.detection import Detection
from app import db
from app.services.detection_service import DetectionService

class CameraService:
   
   
    # 验证摄像头数据的完整性和合法性
    @staticmethod
    def validate_camera_data(data):
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


    # 测试摄像头连接是否正常
    @staticmethod
    def test_camera_connection(url):
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            raise ConnectionError("Failed to connect to camera")
        ret, _ = cap.read()
        cap.release()
        if not ret:
            raise ConnectionError("Failed to read frame from camera")
        return True



    # 添加摄像头并建立与detection的关联
    @staticmethod
    def add_camera(data):
        try:
            # 验证数据
            CameraService.validate_camera_data(data)
            
            # 验证禁停区域数据
            restricted_areas = data.get('restricted_areas', [])
            if not isinstance(restricted_areas, list):
                raise ValueError("Invalid restricted areas format")
                
            for area in restricted_areas:
                if not all(isinstance(point, list) and len(point) == 2 
                          for point in area.get('points', [])):
                    raise ValueError("Invalid area points format")
            
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
                tracking_config=data.get('tracking_config', 'botsort.yaml'),  # 默认跟踪配置
                status='online',
                restricted_areas=restricted_areas
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



    # 启动视频流处理
    @staticmethod
    def start_video_processing(camera):
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



    # 获取摄像头的处理后视频流
    @staticmethod
    def get_camera_stream(camera_id):
        camera = Camera.query.get_or_404(camera_id)
        detection = Detection.query.filter_by(camera_id=camera_id).first()
        
        if not detection or not detection.video_path:
            raise ValueError("No video stream available")
            
        return {
            "stream_url": f"/streams/{camera_id}/live.mp4",
            "camera_status": camera.status
        }



    # 删除摄像头及其相关资源
    @staticmethod
    def delete_camera(camera_id):
        try:
            # 查找摄像头
            camera = Camera.query.get_or_404(camera_id)
            
            # 获取相关的检测记录
            detections = Detection.query.filter_by(camera_id=camera_id).all()
            
            # 删除视频文件
            video_dir = f"streams/{camera_id}"
            if os.path.exists(video_dir):
                for detection in detections:
                    if detection.video_path and os.path.exists(detection.video_path):
                        try:
                            os.remove(detection.video_path)
                        except OSError as e:
                            print(f"Error deleting video file: {e}")
                try:
                    os.rmdir(video_dir)
                except OSError as e:
                    print(f"Error deleting video directory: {e}")
            
            # 从数据库中删除检测记录
            for detection in detections:
                db.session.delete(detection)
            
            # 从数据库中删除摄像头记录
            db.session.delete(camera)
            db.session.commit()
            
            return {"success": True, "message": "Camera and related resources deleted successfully"}
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete camera: {str(e)}")

    @staticmethod
    def update_restricted_areas(camera_id, areas):
        """更新摄像头的禁停区域"""
        try:
            camera = Camera.query.get_or_404(camera_id)
            
            # 验证区域数据格式
            if not isinstance(areas, list):
                raise ValueError("Invalid areas format")
                
            for area in areas:
                if not all(isinstance(point, list) and len(point) == 2 
                          for point in area.get('points', [])):
                    raise ValueError("Invalid area points format")
            
            # 更新禁停区域
            camera.restricted_areas = areas
            db.session.commit()
            
            return {"success": True, "message": "Restricted areas updated successfully"}
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update restricted areas: {str(e)}")
