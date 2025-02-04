"""
车辆检测相关接口

包括：
1. 启动检测接口
2. 查询检测记录接口
3. 分析外部文件接口


"""

from flask import Blueprint, request, jsonify, send_file
from app.services.detection_service import DetectionService
from app.utils.websocket_utils import VideoStreamConfig

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

@detection_blueprint.route('/special-vehicles/config', methods=['POST'])
def configure_special_vehicles():
    """配置特殊车辆"""
    try:
        config = request.json
        # 验证配置格式
        if not isinstance(config, dict):
            return jsonify({"error": "Invalid configuration format"}), 400
            
        for cls_id, settings in config.items():
            if not isinstance(settings, dict) or 'name' not in settings or 'color' not in settings:
                return jsonify({"error": f"Invalid configuration for class {cls_id}"}), 400
        
        # 保存配置到数据库或缓存中
        # ... (根据实际需求实现存储逻辑)
        
        return jsonify({
            "success": True,
            "message": "Special vehicles configuration updated"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@detection_blueprint.route('/stream/config', methods=['POST'])
def configure_stream():
    """配置视频流参数"""
    try:
        config = request.json
        
        # 验证并更新配置
        if 'max_width' in config:
            VideoStreamConfig.MAX_WIDTH = max(640, min(1920, int(config['max_width'])))
        if 'max_height' in config:
            VideoStreamConfig.MAX_HEIGHT = max(480, min(1080, int(config['max_height'])))
        if 'jpeg_quality' in config:
            VideoStreamConfig.JPEG_QUALITY = max(1, min(100, int(config['jpeg_quality'])))
        if 'target_fps' in config:
            VideoStreamConfig.TARGET_FPS = max(1, min(30, int(config['target_fps'])))
            
        return jsonify({
            'success': True,
            'message': 'Stream configuration updated',
            'config': {
                'max_width': VideoStreamConfig.MAX_WIDTH,
                'max_height': VideoStreamConfig.MAX_HEIGHT,
                'jpeg_quality': VideoStreamConfig.JPEG_QUALITY,
                'target_fps': VideoStreamConfig.TARGET_FPS
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400



