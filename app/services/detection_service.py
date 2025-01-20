"""
车辆检测服务

"""

from app.utils.yolo_integration import detect_vehicles
from app.models.detection import DetectionRecord
from app import db

abnormal_vehicle_types = ['oil_tanker', 'heavy_truck']

def process_detection(image_path):
    vehicles = detect_vehicles(image_path)
    for vehicle in vehicles:
        is_abnormal = vehicle['type'] in abnormal_vehicle_types
        record = DetectionRecord(vehicle_type=vehicle['type'], timestamp=vehicle['time'], image_path=image_path, is_abnormal=is_abnormal)
        db.session.add(record)
    db.session.commit()
    return vehicles



