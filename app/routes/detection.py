"""
车辆检测相关接口
"""

from flask import Blueprint, request, jsonify
from app.services.detection_service import process_detection
import cv2

bp = Blueprint('detection', __name__, url_prefix='/detection')

@bp.route('/add_camera', methods=['POST'])
def add_camera():
    camera_url = request.json['camera_url']
    cap = cv2.VideoCapture(camera_url)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        process_detection(frame)
    cap.release()
    return jsonify({'message': 'Camera added successfully'}), 200

@bp.route('/analyze', methods=['POST'])
def analyze_file():
    file = request.files['file']
    file_path = f'uploads/{file.filename}'
    file.save(file_path)
    vehicles = process_detection(file_path)
    return jsonify({'vehicles': vehicles}), 200

