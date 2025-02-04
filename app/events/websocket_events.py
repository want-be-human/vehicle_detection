from flask_socketio import emit
from app.utils.websocket_utils import socketio
from app.services.statistics_service import StatisticsService

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

@socketio.on('connect', namespace='/video')
def handle_video_connect():
    """处理视频流连接"""
    print('Client connected to video stream')

@socketio.on('disconnect', namespace='/video')
def handle_video_disconnect():
    """处理视频流断开连接"""
    print('Client disconnected from video stream')

@socketio.on('join_stream', namespace='/video')
def handle_join_stream(data):
    """处理加入视频流房间"""
    camera_id = data.get('camera_id')
    if camera_id:
        # 将客户端加入到对应摄像头的视频流房间
        room = f'camera_{camera_id}'
        socketio.join_room(room, namespace='/video')
        emit('joined_stream', {'camera_id': camera_id}, namespace='/video')

@socketio.on('leave_stream', namespace='/video')
def handle_leave_stream(data):
    """处理离开视频流房间"""
    camera_id = data.get('camera_id')
    if camera_id:
        room = f'camera_{camera_id}'
        socketio.leave_room(room, namespace='/video')
        emit('left_stream', {'camera_id': camera_id}, namespace='/video')

@socketio.on('connect', namespace='/statistics')
def handle_stats_connect():
    """处理统计数据连接"""
    print('Client connected to statistics namespace')
    # 发送最新统计数据
    today_stats = StatisticsService.calculate_daily_statistics()
    if today_stats:
        emit('statistics_update', today_stats)

@socketio.on('disconnect', namespace='/statistics')
def handle_stats_disconnect():
    """处理统计数据断开连接"""
    print('Client disconnected from statistics namespace')
