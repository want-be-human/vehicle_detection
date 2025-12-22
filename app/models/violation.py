from app import db
from datetime import datetime
from typing import Optional

class Violation(db.Model):
    __tablename__ = 'violations'

    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'), nullable=False)
    camera_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    vehicle_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)  # 格式: {"x": x, "y": y}
    violation_type = db.Column(db.String(50), default='parking')  # 违规类型: parking/speed/etc
    area_id = db.Column(db.Integer)  # 关联的禁停区域ID

    def __init__(self, camera_id: int, camera_name: str, timestamp: datetime,
                 vehicle_type: str, location: str, violation_type: str = 'parking',
                 area_id: Optional[int] = None):
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.timestamp = timestamp
        self.vehicle_type = vehicle_type
        self.location = location
        self.violation_type = violation_type
        self.area_id = area_id

    def to_dict(self):
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'camera_name': self.camera_name,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'vehicle_type': self.vehicle_type,
            'location': self.location,
            'violation_type': self.violation_type,
            'area_id': self.area_id
        }
