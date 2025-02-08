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
   - 数据: {
       'camera_id': 摄像头ID,
       'frame': base64编码的帧数据,
       'timestamp': 时间戳
   }
   - 接收: socket.on('video_frame')

2. 违规提醒 (/violations):
   - 发送: emit_violation_alert()
   - 数据: {
       'camera_id': 摄像头ID,
       'violation_type': 违规类型,
       'location': 位置信息,
       'timestamp': 时间戳
   }
   - 接收: socket.on('violation_alert')

3. 摄像头状态 (/cameras):
   - 发送: emit_camera_status()
   - 数据: {
       'camera_id': 摄像头ID,
       'status': 状态(online/offline/error)
   }
   - 接收: socket.on('camera_status')

4. 统计信息 (/statistics):
   - 发送: emit_detection_stats()
   - 数据: {
       'vehicle_count': 车辆统计,
       'peak_hours': 高峰期,
       'timestamp': 时间戳
   }
   - 接收: socket.on('detection_stats')

配置管理：
VideoStreamConfig:
  - MAX_WIDTH: 1280 - 限制视频帧最大宽度
  - MAX_HEIGHT: 720 - 限制视频帧最大高度
  - JPEG_QUALITY: 80 - JPEG压缩质量(0-100)
  - TARGET_FPS: 25 - 目标帧率，控制传输频率

数据流向：
1. 视频流：
   DetectionService 
   -> emit_video_frame() 
   -> 压缩/编码 
   -> WebSocket
   -> Frontend播放

2. 违规提醒：
   ViolationService 
   -> emit_violation_alert() 
   -> WebSocket 
   -> Frontend提示

3. 状态更新：
   CameraService 
   -> emit_camera_status() 
   -> WebSocket 
   -> Frontend显示

4. 统计数据：
   StatisticsService 
   -> emit_detection_stats() 
   -> WebSocket 
   -> Frontend图表

性能优化：
1. 图像压缩：
   - 限制最大分辨率
   - JPEG压缩
   - 控制帧率

2. 数据分发：
   - 使用房间机制
   - 按摄像头ID分组
   - 避免无效广播

异常处理：
- WebSocket连接异常
- 数据发送失败
- 编码解码错误

使用示例：
1. 发送违规提醒：
   emit_violation_alert({
       'camera_id': 1,
       'violation_type': 'parking',
       'location': {'x': 100, 'y': 200}
   })

2. 推送视频帧：
   emit_video_frame(camera_id=1, frame_data=frame)
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
import cv2
import base64
import time

socketio = SocketIO()

class VideoStreamConfig:
    # 视频流配置
    MAX_WIDTH = 1280  # 最大宽度
    MAX_HEIGHT = 720  # 最大高度
    JPEG_QUALITY = 80  # JPEG压缩质量(0-100)
    TARGET_FPS = 25   # 目标帧率

def emit_violation_alert(violation_data):
    """发送违规提醒到前端"""
    try:
        # 发送到特定摄像头的房间
        camera_id = violation_data.get('camera_id')
        if camera_id:
            room = f'camera_{camera_id}'
            socketio.emit('violation_alert', violation_data, 
                        namespace='/violations', room=room)
        else:
            # 如果没有指定摄像头，广播给所有客户端
            socketio.emit('violation_alert', violation_data, 
                        namespace='/violations')
    except Exception as e:
        print(f"Error sending violation alert: {str(e)}")

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
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 发送到对应摄像头的房间
        room = f'camera_{camera_id}'
        socketio.emit('video_frame', {
            'camera_id': camera_id,
            'frame': frame_base64,
            'timestamp': time.time()
        }, namespace='/video', room=room)
        
    except Exception as e:
        print(f"Error sending video frame: {str(e)}")
