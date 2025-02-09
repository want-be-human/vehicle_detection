"""
WebSocket事件处理模块 (websocket_events.py)

主要功能:
1. 管理四个WebSocket命名空间:
   - /violations: 处理违规提醒和特殊车辆通知
   - /video: 处理实时视频流传输
   - /statistics: 处理实时统计数据
   - /cameras: 处理摄像头状态变更

2. 事件处理:
   - 连接/断开事件：管理客户端连接状态
   - 房间管理：支持按摄像头ID分组接收数据
   - 数据推送：实时推送检测结果到前端

3. 数据流向:
   - 违规检测：[`ViolationService`] -> WebSocket -> 前端提醒
   - 视频流：[`DetectionService`] -> WebSocket -> 前端展示  
   - 统计数据：[`StatisticsService`] -> WebSocket -> 前端图表
   - 摄像头状态：[`CameraService`] -> WebSocket -> 前端显示

命名空间说明：
1. /violations:
   - 事件：connect/disconnect/join/violation_alert/special_vehicle_alert
   - 用途：处理违规提醒和特殊车辆通知
   - 数据格式：{camera_id, violation_type, location, timestamp}

2. /video:
   - 事件：connect/disconnect/join_stream/leave_stream/video_frame
   - 用途：处理实时视频流传输
   - 数据格式：{camera_id, frame(base64), timestamp}

3. /statistics:
   - 事件：connect/disconnect/detection_stats/statistics_update
   - 用途：处理统计数据实时更新
   - 数据格式：{vehicle_count, peak_hours, timestamp}

4. /cameras:
   - 事件：connect/disconnect/camera_status/streaming_start/streaming_stop
   - 用途：处理摄像头状态变更
   - 数据格式：{camera_id, status, timestamp}

相关服务:
- [`ViolationService`](app/services/violation_service.py): 违规检测
- [`DetectionService`](app/services/detection_service.py): 视频检测
- [`StatisticsService`](app/services/statistics_service.py): 统计服务
- [`CameraService`](app/services/camera_service.py): 摄像头管理

使用说明:
1. 前端连接:
   ```javascript
   const socket = io('/namespace');
   socket.on('event_name', (data) => {
     // 处理接收到的数据
   });
   ```

2. 加入摄像头房间:
   ```javascript
   socket.emit('join', {camera_id: 1});
   ```

3. 接收实时数据:
   ```javascript
   socket.on('video_frame', (frame) => {
     // 显示视频帧
   });
   ```

异常处理:
- 连接断开自动重连
- 发送失败重试机制
- 错误事件统一处理
"""

from flask_socketio import emit
from app.utils.websocket_utils import socketio
from app.services.statistics_service import StatisticsService

def _log_connection_status(status, namespace):
    """记录客户端连接状态变化"""
    print(f"Client {status} {namespace} namespace")

# ---------- 违规提醒命名空间(/violations) ----------

@socketio.on('connect', namespace='/violations')
def handle_connect():
    """
    处理违规提醒命名空间的连接事件
    用于建立违规提醒的WebSocket连接
    """
    _log_connection_status("connected to", "/violations")

@socketio.on('disconnect', namespace='/violations')
def handle_disconnect():
    """
    处理违规提醒命名空间的断开事件
    清理相关资源
    """
    _log_connection_status("disconnected from", "/violations")

@socketio.on('join', namespace='/violations')
def handle_join(data):
    """
    处理加入摄像头房间事件
    Args:
        data: 包含camera_id的字典
    用于接收特定摄像头的违规提醒
    """
    camera_id = data.get('camera_id')
    if camera_id:
        socketio.join_room(f'camera_{camera_id}', namespace='/violations')
        emit('joined', {'camera_id': camera_id}, namespace='/violations')

@socketio.on('violation_alert', namespace='/violations')
def handle_violation_alert(data):
    """
    处理违规提醒事件
    Args:
        data: 违规信息字典
    广播违规提醒给所有订阅者
    """
    emit('violation_alert', data, broadcast=True)

@socketio.on('special_vehicle_alert', namespace='/violations')
def handle_special_vehicle_alert(data):
    """
    处理特殊车辆提醒事件
    Args:
        data: 特殊车辆信息字典
    广播特殊车辆提醒给所有订阅者
    """
    emit('special_vehicle_alert', data, broadcast=True)

@socketio.on('error', namespace='/violations')
def handle_violation_error(error_data):
    """处理违规检测错误事件"""
    emit('violation_error', error_data, broadcast=True)

# ---------- 视频流命名空间(/video) ----------

@socketio.on('connect', namespace='/video')
def handle_video_connect():
    """处理视频流连接事件"""
    _log_connection_status("connected to", "/video")

@socketio.on('disconnect', namespace='/video')
def handle_video_disconnect():
    """处理视频流断开事件"""
    _log_connection_status("disconnected from", "/video")

@socketio.on('join_stream', namespace='/video')
def handle_join_stream(data):
    """
    处理加入视频流房间事件
    Args:
        data: 包含camera_id的字典
    用于接收特定摄像头的视频流
    """
    camera_id = data.get('camera_id')
    if camera_id:
        room = f'camera_{camera_id}'
        socketio.join_room(room, namespace='/video')
        emit('joined_stream', {'camera_id': camera_id}, namespace='/video')

@socketio.on('leave_stream', namespace='/video')
def handle_leave_stream(data):
    """
    处理离开视频流房间事件
    Args:
        data: 包含camera_id的字典
    停止接收特定摄像头的视频流
    """
    camera_id = data.get('camera_id')
    if camera_id:
        room = f'camera_{camera_id}'
        socketio.leave_room(room, namespace='/video')
        emit('left_stream', {'camera_id': camera_id}, namespace='/video')

@socketio.on('video_frame', namespace='/video')
def handle_video_frame(data):
    """
    处理视频帧事件
    Args:
        data: 包含camera_id和frame数据的字典
    将视频帧发送到对应的房间
    """
    camera_id = data.get('camera_id')
    if camera_id:
        room = f'camera_{camera_id}'
        emit('video_frame', data, room=room)

@socketio.on('error', namespace='/video')
def handle_video_error(error_data):
    """处理视频流错误事件"""
    emit('video_error', error_data, broadcast=True)

# ---------- 统计数据命名空间(/statistics) ----------

@socketio.on('connect', namespace='/statistics')
def handle_stats_connect():
    """
    处理统计数据连接事件
    连接时自动发送最新统计数据
    """
    _log_connection_status("connected to", "/statistics")
    today_stats = StatisticsService.calculate_daily_statistics()
    if today_stats:
        emit('statistics_update', today_stats)

@socketio.on('disconnect', namespace='/statistics')
def handle_stats_disconnect():
    """处理统计数据断开事件"""
    _log_connection_status("disconnected from", "/statistics")

@socketio.on('detection_stats', namespace='/statistics')
def handle_detection_stats(data):
    """
    处理检测统计事件
    Args:
        data: 统计数据字典
    广播统计数据给所有订阅者
    """
    emit('detection_stats', data, broadcast=True)

@socketio.on('statistics_update', namespace='/statistics')
def handle_statistics_update(data):
    """
    处理统计数据更新事件
    Args:
        data: 更新的统计数据
    广播更新的统计数据
    """
    emit('statistics_update', data, broadcast=True)

@socketio.on('error', namespace='/statistics')
def handle_stats_error(error_data):
    """处理统计数据错误事件"""
    emit('statistics_error', error_data, broadcast=True)

# ---------- 摄像头状态命名空间(/cameras) ----------

@socketio.on('camera_status', namespace='/cameras')
def handle_camera_status(data):
    """
    处理摄像头状态更新事件
    Args:
        data: 摄像头状态信息
    广播摄像头状态变化
    """
    emit('camera_status', data, broadcast=True)

@socketio.on('connect', namespace='/cameras')
def handle_cameras_connect():
    """处理摄像头状态连接事件"""
    _log_connection_status("connected to", "/cameras")

@socketio.on('disconnect', namespace='/cameras')
def handle_cameras_disconnect():
    """处理摄像头状态断开事件"""
    _log_connection_status("disconnected from", "/cameras")

@socketio.on('streaming_start', namespace='/cameras')
def handle_streaming_start(data):
    """
    处理开始视频流事件
    Args:
        data: 包含camera_id的字典
    """
    camera_id = data.get('camera_id')
    if camera_id:
        emit('streaming_started', {'camera_id': camera_id}, broadcast=True)

@socketio.on('streaming_stop', namespace='/cameras')
def handle_streaming_stop(data):
    """
    处理停止视频流事件
    Args:
        data: 包含camera_id的字典
    """
    camera_id = data.get('camera_id')
    if camera_id:
        emit('streaming_stopped', {'camera_id': camera_id}, broadcast=True)

@socketio.on('error', namespace='/cameras')
def handle_camera_error(error_data):
    """处理摄像头错误事件"""
    emit('camera_error', error_data, broadcast=True)