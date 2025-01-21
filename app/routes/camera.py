"""
管理摄像头api接口
包含获取所有摄像头、新增摄像头、删除摄像头
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
