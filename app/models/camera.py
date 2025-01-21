"""
摄像头数据库模型
存储摄像头信息：名称、IP地址、端口、URL、分辨率、帧率、编码格式、YOLO模型路径、跟踪算法配置路径

"""

from app import db

class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    resolution = db.Column(db.String(50))
    frame_rate = db.Column(db.Integer)
    encoding_format = db.Column(db.String(50))
    model = db.Column(db.String(255))  # YOLO模型路径
    tracking_config = db.Column(db.String(255))  # 跟踪算法配置路径

    def __repr__(self):
        return f"<Camera {self.name} ({self.ip_address}:{self.port})>"
