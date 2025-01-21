"""
车辆检测相关接口

包括：
1. 启动检测接口
2. 查询检测记录接口
3. 分析外部文件接口


"""

from flask import Blueprint, request, jsonify
from app.services.detection_service import DetectionService

detection_blueprint = Blueprint('detection', __name__)

@detection_blueprint.route('/detect', methods=['POST'])
def start_detection():
    """
    启动检测接口
    请求体包括：摄像头ID、模型路径、跟踪算法配置路径
    """
    data = request.json
    DetectionService.start_detection(data)
    return jsonify({"message": "Detection started"}), 200

@detection_blueprint.route('/detections', methods=['GET'])
def get_detections():
    """
    查询检测记录接口
    """
    detections = DetectionService.get_all_detections()
    return jsonify(detections), 200

@detection_blueprint.route('/analyze', methods=['POST'])
def analyze_file():
    """
    分析外部文件接口
    请求体包括：文件路径、模型路径、跟踪算法配置路径
    响应包括：分析结果
    """
    data = request.json
    results = DetectionService.analyze_file(data)
    return jsonify({"message": "File analyzed successfully", "results": results}), 200



