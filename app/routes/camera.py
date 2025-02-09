"""
摄像头管理接口模块 (camera.py)

主要功能：
1. 摄像头管理API：
   - 添加新摄像头
   - 删除现有摄像头
   - 更新摄像头配置

REST API接口：
1. 添加摄像头：
   POST /cameras
   请求体格式：
   {
     "name": "摄像头1",
     "ip_address": "192.168.1.100",
     "port": 554,
     "url": "rtsp://192.168.1.100:554/stream1",
     "resolution": "1920x1080",
     "frame_rate": 30,
     "encoding_format": "H.264",
     "restricted_areas": [
       {
         "id": 1,
         "points": [[100,100], [200,100], [200,200], [100,200]]
       }
     ]
   }
   响应：201 Created
   {
     "message": "Camera added successfully"
   }

2. 删除摄像头：
   DELETE /cameras/<camera_id>
   响应：200 OK
   {
     "message": "Camera deleted successfully"
   }

工作流程：
1. 添加摄像头：
   Frontend POST请求 
   -> CameraService.add_camera()
   -> 验证数据
   -> 创建Camera记录
   -> 启动视频处理
   -> 返回结果

2. 删除摄像头：
   Frontend DELETE请求
   -> CameraService.delete_camera()
   -> 停止视频处理
   -> 删除相关资源
   -> 清理数据库记录
   -> 返回结果

与其他模块关联：
- [`CameraService`](app/services/camera_service.py): 摄像头管理服务
- [`Camera`](app/models/camera.py): 摄像头数据模型
- [`DetectionService`](app/services/detection_service.py): 检测服务
- [`WebSocket`](app/utils/websocket_utils.py): 实时状态推送

异常处理：
- 400: 请求参数错误
- 404: 摄像头不存在
- 500: 服务器内部错误
"""

# 摄像头管理接口
from flask import Blueprint, request, jsonify
from app.services.camera_service import CameraService

camera_blueprint = Blueprint('camera', __name__)

@camera_blueprint.route('/cameras', methods=['POST'])
def add_camera():
    """
    添加摄像头接口
    请求体包括：名称、IP地址、端口号、URL、分辨率、帧率、编码格式
    """
    data = request.json
    CameraService.add_camera(data)
    return jsonify({"message": "Camera added successfully"}), 201

@camera_blueprint.route('/cameras/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    """
    删除摄像头接口
    """
    CameraService.delete_camera(camera_id)
    return jsonify({"message": "Camera deleted successfully"}), 200
