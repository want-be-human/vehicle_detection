"""
摄像头数据库模型
存储摄像头信息：名称、IP地址、端口、URL、分辨率、帧率、编码格式、模型路径、跟踪算法配置路径、是否启用、状态等、关联的检测记录、警告信息等、违规信息等、反向引用

"""

from app import db

class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    ip_address = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(255), nullable=False)

    resolution = db.Column(db.String(50)) #分辨率
    frame_rate = db.Column(db.Integer) #帧率
    encoding_format = db.Column(db.String(50)) #编码格式

    model = db.Column(db.String(255))  # 模型路径
    tracking_config = db.Column(db.String(255))  # 跟踪算法配置路径

    is_active = db.Column(db.Boolean, default=True)  # 摄像头是否启用
    status = db.Column(db.String(20), default='offline')  # 摄像头状态: online/offline/error
    
    # 关联的检测记录反向引用
    detections = db.relationship('Detection', backref='camera', lazy=True)
    detection_records = db.relationship('DetectionModel', backref='camera', lazy=True)
    

    def __repr__(self):
        return f"<Camera {self.name} ({self.ip_address}:{self.port})>"
