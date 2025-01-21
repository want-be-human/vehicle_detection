"""
数据查询相关接口

- 查询历史监控接口

"""
from flask import Blueprint, request, jsonify
from app.services.history_service import HistoryService

# 创建Blueprint实例
history_blueprint = Blueprint('history', __name__)

@history_blueprint.route('/query', methods=['POST'])
def query_history():
    """
    查询历史监控接口
    请求体包括：年、月、日、时、摄像头ID
    响应包括：对应视频的URL或路径
    """
    data = request.json
    video_url = HistoryService.query_video(data)
    if video_url:
        return jsonify({"message": "Query successful", "video_url": video_url}), 200
    return jsonify({"message": "No video found for the specified time and camera"}), 404

