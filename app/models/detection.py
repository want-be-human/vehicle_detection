"""
车辆检测记录数据库模型
"""

from app import db

class DetectionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    image_path = db.Column(db.String(200), nullable=True)
    is_abnormal = db.Column(db.Boolean, default=False)

