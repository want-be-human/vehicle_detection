from unittest.mock import Mock, patch

import pytest

from app.services.auth_service import authenticate_user
from app.services.camera_service import CameraService
from app.services.violation_service import ViolationService

try:
    from app.services.detection_service import DetectionService
    DETECTION_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - optional dependency guard
    DetectionService = None
    DETECTION_IMPORT_ERROR = exc


class TestCameraService:
    def test_validate_camera_data_success(self):
        valid_data = {
            'name': '测试摄像头',
            'ip_address': '192.168.1.100',
            'port': 554,
            'url': 'rtsp://192.168.1.100:554/stream',
            'resolution': '1920x1080',
            'frame_rate': 30,
            'encoding_format': 'H.264'
        }

        assert CameraService.validate_camera_data(valid_data) is True

    def test_validate_camera_data_missing_field(self):
        invalid_data = {
            'name': '测试摄像头',
            'ip_address': '192.168.1.100'
        }

        with pytest.raises(ValueError, match="Missing required field"):
            CameraService.validate_camera_data(invalid_data)

    def test_validate_camera_data_invalid_ip(self):
        invalid_data = {
            'name': '测试摄像头',
            'ip_address': '999.999.999.999',
            'port': 554,
            'url': 'rtsp://test/stream',
            'resolution': '1920x1080',
            'frame_rate': 30,
            'encoding_format': 'H.264'
        }

        with pytest.raises(ValueError, match="Invalid IP address"):
            CameraService.validate_camera_data(invalid_data)

    @patch('app.services.camera_service.cv2.VideoCapture')
    def test_test_camera_connection_success(self, mock_video_capture):
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "frame_data")
        mock_video_capture.return_value = mock_cap

        assert CameraService.test_camera_connection("rtsp://test/stream") is True

    @patch('app.services.camera_service.cv2.VideoCapture')
    def test_test_camera_connection_failure(self, mock_video_capture):
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap

        with pytest.raises(ConnectionError, match="Failed to connect"):
            CameraService.test_camera_connection("rtsp://test/stream")


@pytest.mark.skipif(DetectionService is None, reason=f"DetectionService unavailable: {DETECTION_IMPORT_ERROR}")
class TestDetectionService:
    @patch('app.services.detection_service.emit_streaming_result')
    @patch('app.services.detection_service.YOLOIntegration')
    @patch('app.services.detection_service.threading.Thread')
    def test_start_detection_success(self, mock_thread, mock_yolo, mock_emit, tmp_path):
        process_thread = Mock()
        cleanup_thread = Mock()
        mock_thread.side_effect = [process_thread, cleanup_thread]

        test_data = {
            'camera_id': 1,
            'stream_url': 'rtsp://test/stream',
            'model_path': 'yolov8n.pt',
            'save_dir': tmp_path.as_posix(),
            'retention_days': 30
        }

        result = DetectionService.start_detection(test_data)

        assert result['success'] is True
        assert result['camera_id'] == 1
        assert result['retention_days'] == 30
        assert mock_thread.call_count == 2
        DetectionService.active_threads.clear()

    def test_start_detection_duplicate_camera(self, tmp_path):
        DetectionService.active_threads[1] = {'thread': Mock(), 'status': 'running'}

        test_data = {
            'camera_id': 1,
            'stream_url': 'rtsp://test/stream',
            'model_path': 'yolov8n.pt',
            'save_dir': tmp_path.as_posix()
        }

        result = DetectionService.start_detection(test_data)

        assert result['success'] is False
        assert "already being processed" in result['message']
        DetectionService.active_threads.clear()


class TestViolationService:
    def test_check_violations_no_camera(self):
        service = ViolationService()

        with patch('app.services.violation_service.Camera.query.get', return_value=None):
            assert service.check_violations(999, {}) == []

    def test_check_violations_no_restricted_areas(self):
        service = ViolationService()
        mock_camera = Mock()
        mock_camera.restricted_areas = None

        with patch('app.services.violation_service.Camera.query.get', return_value=mock_camera):
            assert service.check_violations(1, {}) == []

    @patch('app.services.violation_service.ViolationDetector.check_vehicle_violation')
    def test_check_violations_with_violation(self, mock_check):
        service = ViolationService()
        mock_camera = Mock()
        mock_camera.id = 1
        mock_camera.name = "测试摄像头"
        mock_camera.restricted_areas = [{"id": 1, "points": [[0, 0], [100, 0], [100, 100], [0, 100]]}]

        mock_check.return_value = [{
            'track_id': 123,
            'vehicle_type': 'car',
            'location': {'x': 50, 'y': 50},
            'area_id': 1
        }]

        with patch('app.services.violation_service.Camera.query.get', return_value=mock_camera):
            with patch('app.services.violation_service.db.session.add'):
                with patch('app.services.violation_service.db.session.commit'):
                    violations = service.check_violations(1, {})

        assert len(violations) == 1
        assert violations[0]['vehicle_type'] == 'car'


class TestAuthService:
    def test_authenticate_user_success(self):
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = 'admin'
        mock_user.password = 'hashed_password'

        with patch('app.services.auth_service.User.query.filter_by', return_value=Mock(first=Mock(return_value=mock_user))):
            with patch('werkzeug.security.check_password_hash', return_value=True):
                with patch('app.services.auth_service.jwt.encode', return_value='fake_token'):
                    success, token = authenticate_user('admin', 'password123')

        assert success is True
        assert token == 'fake_token'

    def test_authenticate_user_wrong_password(self):
        mock_user = Mock()
        mock_user.password = 'hashed_password'

        with patch('app.services.auth_service.User.query.filter_by', return_value=Mock(first=Mock(return_value=mock_user))):
            with patch('werkzeug.security.check_password_hash', return_value=False):
                success, token = authenticate_user('admin', 'wrong_password')

        assert success is False
        assert token is None

    def test_authenticate_user_not_found(self):
        with patch('app.services.auth_service.User.query.filter_by', return_value=Mock(first=Mock(return_value=None))):
            success, token = authenticate_user('nonexistent', 'password')

        assert success is False
        assert token is None
