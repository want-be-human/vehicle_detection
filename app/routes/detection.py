"""
车辆检测相关接口

包括：
1. 启动检测接口
2. 查询检测记录接口
3. 分析外部文件接口


"""

from flask import Blueprint, request, jsonify, send_file
from app.services.detection_service import DetectionService

detection_blueprint = Blueprint('detection', __name__)

@detection_blueprint.route('/detect', methods=['POST'])
def start_detection():
    """
    启动检测接口
    请求体包括：
            - camera_id: 摄像头ID
            - stream_url: 视频流URL
            - model_path: YOLO模型路径
            - tracking_config: 跟踪配置路径
            - output_path: 输出视频路径
            - retention_days: 视频保存天数

    响应包括：检测结果
    """
    data = request.json
    # 添加retention_days参数
    if 'retention_days' not in data:
        data['retention_days'] = 30  # 默认30天
    result = DetectionService.start_detection(data)
    return jsonify(result), 200

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
    return jsonify(results), 200

@detection_blueprint.route('/results/<path:filename>')
def get_results(filename):
    """获取处理结果文件"""
    try:
        return send_file(filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@detection_blueprint.route('/status', methods=['GET'])
def get_processing_status():
    """获取所有处理线程的状态"""
    status = DetectionService.get_processing_status()
    return jsonify(status), 200



