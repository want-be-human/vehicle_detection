from flask import Blueprint, send_file, request
import os

bp = Blueprint('detection', __name__, url_prefix='/detection')

@bp.route('/video', methods=['GET'])
def get_video():
    camera_id = request.args.get('camera_id')
    timestamp = request.args.get('timestamp')  # Format: YYYYMMDDHH
    file_path = os.path.join('processed_videos', f"{camera_id}_{timestamp}.avi")

    if not os.path.exists(file_path):
        return {'message': 'Video not found'}, 404

    return send_file(file_path, as_attachment=True)
