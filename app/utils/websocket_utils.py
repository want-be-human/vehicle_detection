from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO()

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
