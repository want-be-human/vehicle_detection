from unittest.mock import Mock, patch

from app.events import websocket_events as events


@patch('app.events.websocket_events._log_connection_status')
def test_handle_connect(mock_log):
    events.handle_connect()
    mock_log.assert_called_with("connected to", "/violations")


@patch('app.events.websocket_events._log_connection_status')
def test_handle_disconnect(mock_log):
    events.handle_disconnect()
    mock_log.assert_called_with("disconnected from", "/violations")


@patch('app.events.websocket_events.emit')
def test_handle_violation_alert(mock_emit):
    test_data = {
        "camera_id": 1,
        "violation_type": "parking",
        "location": {"x": 100, "y": 200},
        "timestamp": "2024-03-15 14:30:00"
    }

    events.handle_violation_alert(test_data)

    mock_emit.assert_called_with('violation_alert', test_data, broadcast=True)


@patch('app.events.websocket_events.socketio')
def test_handle_join_stream(mock_socketio):
    events.handle_join_stream({"camera_id": 1})
    mock_socketio.join_room.assert_called_with('camera_1', namespace='/video')


@patch('app.events.websocket_events.emit')
def test_handle_video_frame(mock_emit):
    events.handle_video_frame({"camera_id": 2, "frame": "data"})
    mock_emit.assert_called_with('video_frame', {'camera_id': 2, 'frame': 'data'}, room='camera_2')
