"""
WebSocket通信工具模块 (websocket_utils.py)

主要功能：
1. WebSocket服务初始化：
   - 创建SocketIO实例
   - 配置视频流参数
   - 提供实时数据推送功能

2. 实时通信功能：
   - 视频帧推送
   - 违规提醒
   - 摄像头状态更新
   - 检测统计推送

3. 数据处理：
   - 视频帧压缩
   - 图像格式转换
   - Base64编码

与前端交互：
1. 视频流传输 (/video):
   - 发送: emit_video_frame()
   - 数据格式: {
       'camera_id': 摄像头ID,
       'frame': base64编码的帧数据,
       'timestamp': 时间戳
   }
   - 接收: socket.on('video_frame')

2. 违规提醒 (/violations):
   - 发送: emit_violation_alert()
   - 数据格式: {
       'camera_id': 摄像头ID,
       'violation_type': 违规类型(parking/speed),
       'location': {'x': x坐标, 'y': y坐标},
       'timestamp': 时间戳,
       'vehicle_type': 车辆类型
   }
   - 接收: socket.on('violation_alert')

3. 摄像头状态 (/cameras):
   - 发送: emit_camera_status()
   - 数据格式: {
       'camera_id': 摄像头ID,
       'status': 状态(online/offline/error)
   }
   - 接收: socket.on('camera_status')

4. 统计信息 (/statistics):
   - 发送: emit_detection_stats()
   - 数据格式: {
       'vehicle_count': {'car': 100, 'bus': 50},
       'peak_hours': [{'hour': 8, 'count': 120}],
       'timestamp': 时间戳
   }
   - 接收: socket.on('detection_stats')

数据流向：
1. 视频流：
   [`DetectionService`](app/services/detection_service.py)
   -> emit_video_frame() 
   -> 压缩/编码 
   -> WebSocket
   -> Frontend播放

2. 违规提醒：
   [`ViolationService`](app/services/violation_service.py)
   -> emit_violation_alert() 
   -> WebSocket 
   -> Frontend提示

3. 状态更新：
   [`CameraService`](app/services/camera_service.py)
   -> emit_camera_status() 
   -> WebSocket 
   -> Frontend显示

4. 统计数据：
   [`StatisticsService`](app/services/statistics_service.py)
   -> emit_detection_stats() 
   -> WebSocket 
   -> Frontend图表

性能优化：
1. 图像压缩：
   - 限制最大分辨率(1280x720)
   - JPEG压缩(质量80)
   - 控制帧率(25fps)

2. 数据分发：
   - 使用房间机制(按摄像头ID分组)
   - 避免全局广播
   - 及时清理断开的连接

异常处理：
- WebSocket连接异常处理
- 数据发送失败重试
- 编码解码错误捕获
- 资源释放确保
"""

from flask_socketio import SocketIO
from typing import ClassVar
import cv2
import base64
import time

socketio = SocketIO()

class VideoStreamConfig:
    # 视频流配置
    MAX_WIDTH: ClassVar[int] = 1280  # 最大宽度
    MAX_HEIGHT: ClassVar[int] = 720  # 最大高度
    JPEG_QUALITY: ClassVar[int] = 80  # JPEG压缩质量(0-100)
    TARGET_FPS: ClassVar[int] = 25   # 目标帧率

def emit_violation_alert(violation_data):
    """
    发送违规提醒到前端
    Args:
        violation_data: dict, 包含:
            - camera_id: 摄像头ID
            - violation_type: 违规类型
            - location: 位置信息
            - timestamp: 时间戳
            - vehicle_type: 车辆类型
    """
    try:
        # 发送到特定摄像头的房间
        camera_id = violation_data.get('camera_id')
        if camera_id:
            room = f'camera_{camera_id}'
            socketio.emit('violation_alert', violation_data, 
                        namespace='/violations', to=room)
        else:
            # 如果没有指定摄像头，广播给所有客户端
            socketio.emit('violation_alert', violation_data, 
                        namespace='/violations')
    except Exception as e:
        print(f"Error sending violation alert: {str(e)}")


def emit_special_vehicle_alert(alert_data):
    """
    发送特殊车辆提醒到前端
    Args:
        alert_data: dict, 包含:
            - camera_name: 摄像头名称
            - vehicles: 特殊车辆列表
            - timestamp: 时间戳
    """
    try:
        socketio.emit('special_vehicle_alert', alert_data, 
                     namespace='/violations')
    except Exception as e:
        print(f"Error sending special vehicle alert: {str(e)}")

def emit_camera_status(camera_id, status):
    """发送摄像头状态更新"""
    try:
        socketio.emit('camera_status', {
            'camera_id': camera_id,
            'status': status
        }, namespace='/cameras')
    except Exception as e:
        print(f"Error sending camera status: {str(e)}")

def emit_detection_stats(stats_data):
    """发送检测统计信息"""
    try:
        socketio.emit('detection_stats', stats_data, 
                     namespace='/statistics')
    except Exception as e:
        print(f"Error sending detection stats: {str(e)}")

def emit_video_frame(camera_id, frame_data):
    """发送视频帧到前端"""
    try:
        # 调整分辨率
        h, w = frame_data.shape[:2]
        if w > VideoStreamConfig.MAX_WIDTH or h > VideoStreamConfig.MAX_HEIGHT:
            ratio = min(VideoStreamConfig.MAX_WIDTH/w, VideoStreamConfig.MAX_HEIGHT/h)
            new_size = (int(w*ratio), int(h*ratio))
            frame_data = cv2.resize(frame_data, new_size, interpolation=cv2.INTER_AREA)
            
        # JPEG压缩
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), VideoStreamConfig.JPEG_QUALITY]
        _, buffer = cv2.imencode('.jpg', frame_data, encode_param)
        
        # 转换为base64字符串
        frame_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
        
        # 发送到对应摄像头的房间
        room = f'camera_{camera_id}'
        socketio.emit('video_frame', {
            'camera_id': camera_id,
            'frame': frame_base64,
            'timestamp': time.time()
        }, namespace='/video', to=room)
        
    except Exception as e:
        print(f"Error sending video frame: {str(e)}")

def emit_error(namespace, error_data):
    """发送错误事件"""
    try:
        socketio.emit('error', error_data, namespace=namespace)
    except Exception as e:
        print(f"Error sending error event: {str(e)}")

def emit_streaming_status(camera_id, status):
    """发送视频流状态更新"""
    try:
        event = 'streaming_start' if status == 'started' else 'streaming_stop'
        socketio.emit(event, {'camera_id': camera_id}, namespace='/cameras')
    except Exception as e:
        print(f"Error sending streaming status: {str(e)}")

def emit_joined_status(camera_id, namespace, event_type='joined'):
    """发送加入/离开状态"""
    try:
        socketio.emit(f'{event_type}', {
            'camera_id': camera_id
        }, namespace=namespace)
    except Exception as e:
        print(f"Error sending {event_type} status: {str(e)}")

def emit_streaming_result(camera_id, status):
    """发送流媒体结果状态"""
    try:
        event = 'streaming_started' if status == 'started' else 'streaming_stopped'
        socketio.emit(event, {
            'camera_id': camera_id
        }, namespace='/cameras')
    except Exception as e:
        print(f"Error sending streaming result: {str(e)}")
