"""
数据查询相关接口
"""

from flask import Blueprint, request, jsonify, send_file
from app.models.detection import DetectionRecord, Video

bp = Blueprint('data', __name__)

@bp.route('/history_video', methods=['GET'])
def get_history_video():
    timestamp = request.args.get('timestamp')  # 传入查询的时间戳
    video = Video.query.filter_by(timestamp=timestamp).first()
    return jsonify({'video_path': video.video_path}), 200

