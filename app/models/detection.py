"""
车辆检测记录数据库模型

Detection: 车辆检测记录模型
DetectionModel: 车辆检测记录模型（用于存储检测记录）

"""

from app import db

class Detection(db.Model):
    __tablename__ = 'detections'

    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    vehicle_type = db.Column(db.String(100))  # 特殊车辆类型
    location = db.Column(db.String(255))  # 出现位置
    video_path = db.Column(db.String(255))  # 分析后的视频存储路径
    is_violation = db.Column(db.Boolean, default=False)  # 是否违规

    def __repr__(self):
        return f"<Detection {self.vehicle_type} at {self.timestamp}>"

class DetectionModel(db.Model):
    __tablename__ = 'detection_records'
    
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)  # 记录时间
    video_path = db.Column(db.String(255), nullable=False)  # 视频存储路径
    # 其他字段（如检测车辆数量、类型等）

    def __repr__(self):
        return f"<DetectionRecord(camera_id={self.camera_id}, timestamp={self.timestamp})>"

