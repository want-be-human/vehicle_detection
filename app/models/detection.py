"""
车辆检测记录数据库模型

Detection: 车辆检测记录模型
- camera_id: 摄像头ID
- timestamp: 检测时间
- vehicle_type: 特殊车辆类型
- location: 出现位置
- video_path: 分析后的视频存储路径
- is_violation: 是否违规

"""

from app import db

class Detection(db.Model):
    __tablename__ = 'detections'

    id = db.Column(db.Integer, primary_key=True)

    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    video_path = db.Column(db.String(255))  # 分析后的视频存储路径


    vehicle_type = db.Column(db.String(100))  # 特殊车辆类型
    location = db.Column(db.String(255))  # 出现位置
    is_violation = db.Column(db.Boolean, default=False)  # 是否违规

    def __repr__(self):
        return f"<Detection {self.vehicle_type} at {self.timestamp}>"


