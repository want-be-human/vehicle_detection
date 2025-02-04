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
