from flask_socketio import emit
from app.utils.websocket_utils import socketio

@socketio.on('connect', namespace='/violations')
def handle_connect():
    """处理客户端连接"""
    print('Client connected to violations namespace')

@socketio.on('disconnect', namespace='/violations')
def handle_disconnect():
    """处理客户端断开连接"""
    print('Client disconnected from violations namespace')

@socketio.on('join', namespace='/violations')
def handle_join(data):
    """处理客户端加入特定摄像头的房间"""
    camera_id = data.get('camera_id')
    if camera_id:
        # 将客户端加入到对应摄像头的房间
        socketio.join_room(f'camera_{camera_id}', namespace='/violations')
        emit('joined', {'camera_id': camera_id}, namespace='/violations')
