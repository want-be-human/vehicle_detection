"""
摄像头业务逻辑
包含以下功能：
1. 添加摄像头
2. 删除摄像头

"""

# 摄像头管理服务
from app.models.camera import Camera
from app import db

class CameraService:
    @staticmethod
    def add_camera(data):
        """
        添加摄像头逻辑
        TODO: 验证数据的完整性和合法性
        """
        camera = Camera(
            name=data['name'],
            ip_address=data['ip_address'],
            port=data['port'],
            url=data['url'],
            resolution=data['resolution'],
            frame_rate=data['frame_rate'],
            encoding_format=data['encoding_format']
        )
        db.session.add(camera)
        db.session.commit()

    @staticmethod
    def delete_camera(camera_id):
        """
        删除摄像头逻辑
        """
        camera = Camera.query.get_or_404(camera_id)
        db.session.delete(camera)
        db.session.commit()
