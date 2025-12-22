from unittest.mock import Mock, patch

import pytest
from flask import Flask

from app.routes.auth import auth_blueprint
from app.routes.camera import camera_blueprint

try:
    from app.routes.detection import detection_blueprint
    DETECTION_ROUTE_ERROR = None
except Exception as exc:  # pragma: no cover - optional dependency guard
    detection_blueprint = None
    DETECTION_ROUTE_ERROR = exc


@pytest.fixture
def auth_client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(auth_blueprint)
    return app.test_client()


@pytest.fixture
def camera_client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(camera_blueprint, url_prefix='/camera')
    return app.test_client()


@pytest.fixture
def detection_client():
    if detection_blueprint is None:
        pytest.skip(f"Detection routes unavailable: {DETECTION_ROUTE_ERROR}")
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(detection_blueprint, url_prefix='/detection')
    return app.test_client()


class TestAuthRoutes:
    @patch('app.routes.auth.register_user')
    def test_register_success(self, mock_register, auth_client):
        mock_register.return_value = Mock()

        response = auth_client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'password123',
            'role': 'user'
        })

        assert response.status_code == 200
        assert response.get_json()['message'] == 'User registered successfully'

    @patch('app.routes.auth.authenticate_user')
    def test_login_success(self, mock_authenticate, auth_client):
        mock_authenticate.return_value = (True, 'fake_jwt_token')

        response = auth_client.post('/auth/login', json={
            'username': 'admin',
            'password': 'password123'
        })

        assert response.status_code == 200
        assert response.get_json()['token'] == 'fake_jwt_token'

    @patch('app.routes.auth.authenticate_user')
    def test_login_failure(self, mock_authenticate, auth_client):
        mock_authenticate.return_value = (False, None)

        response = auth_client.post('/auth/login', json={
            'username': 'admin',
            'password': 'wrong_password'
        })

        assert response.status_code == 401
        assert response.get_json()['message'] == 'Invalid credentials'


class TestCameraRoutes:
    @patch('app.routes.camera.CameraService.add_camera')
    def test_add_camera_success(self, mock_add, camera_client):
        mock_add.return_value = {"success": True}
        camera_data = {
            "name": "测试摄像头",
            "ip_address": "192.168.1.100",
            "port": 554,
            "url": "rtsp://192.168.1.100:554/stream",
            "resolution": "1920x1080",
            "frame_rate": 30,
            "encoding_format": "H.264"
        }

        response = camera_client.post('/camera/cameras', json=camera_data)

        assert response.status_code == 201
        assert response.get_json()['message'] == 'Camera added successfully'

    @patch('app.routes.camera.CameraService.delete_camera')
    def test_delete_camera_success(self, mock_delete, camera_client):
        mock_delete.return_value = {"success": True}

        response = camera_client.delete('/camera/cameras/1')

        assert response.status_code == 200
        assert response.get_json()['message'] == 'Camera deleted successfully'


@pytest.mark.skipif(detection_blueprint is None, reason=f"Detection routes unavailable: {DETECTION_ROUTE_ERROR}")
class TestDetectionRoutes:
    @patch('app.routes.detection.DetectionService.start_detection')
    def test_start_detection_success(self, mock_detect, detection_client):
        mock_detect.return_value = {
            "success": True,
            "status": "started",
            "camera_id": 1
        }

        detection_data = {
            "camera_id": 1,
            "stream_url": "rtsp://test/stream",
            "model_path": "yolov8n.pt",
            "tracking_config": "botsort.yaml",
            "output_path": "streams/1/live.mp4",
            "retention_days": 30
        }

        response = detection_client.post('/detection/detect', json=detection_data)

        assert response.status_code == 200
        assert response.get_json()['status'] == 'started'

    @patch('app.routes.detection.DetectionService.get_all_detections')
    def test_get_detections(self, mock_get, detection_client):
        mock_get.return_value = [{
            "id": 1,
            "camera_id": 1,
            "timestamp": "2024-03-15 14:30:00",
            "vehicle_type": "car",
            "location": "Gate 1"
        }]

        response = detection_client.get('/detection/detections')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['vehicle_type'] == 'car'
