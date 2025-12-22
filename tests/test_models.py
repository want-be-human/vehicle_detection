from datetime import datetime

from werkzeug.security import generate_password_hash

from app import db
from app.models.camera import Camera
from app.models.detection import Detection
from app.models.user import User
from app.models.violation import Violation


class TestModels:
    """Model layer tests."""

    def test_camera_model(self, app):
        with app.app_context():
            camera = Camera(
                name="测试摄像头",
                ip_address="192.168.1.100",
                port=554,
                url="rtsp://192.168.1.100:554/stream",
                resolution="1920x1080",
                frame_rate=30,
                encoding_format="H.264",
                status="online"
            )

            db.session.add(camera)
            db.session.commit()

            assert camera.id is not None
            assert camera.is_active is True
            assert str(camera) == "<Camera 测试摄像头 (192.168.1.100:554)>"

    def test_detection_model_creation(self, app):
        with app.app_context():
            detection = Detection(
                camera_id=1,
                timestamp=datetime.now(),
                vehicle_type="car",
                location="Gate 1",
                is_violation=False
            )

            db.session.add(detection)
            db.session.commit()

            assert detection.id is not None
            assert detection.vehicle_type == "car"
            assert detection.is_violation is False

    def test_violation_model_to_dict(self, app):
        with app.app_context():
            violation = Violation(
                camera_id=1,
                camera_name="测试摄像头",
                timestamp=datetime.now(),
                vehicle_type="truck",
                location="{'x': 100, 'y': 200}",
                violation_type="parking",
                area_id=1
            )

            data = violation.to_dict()
            assert data['camera_id'] == 1
            assert data['camera_name'] == "测试摄像头"
            assert data['vehicle_type'] == "truck"
            assert 'timestamp' in data

    def test_user_model_authentication(self, app):
        with app.app_context():
            user = User(
                username="testuser",
                password=generate_password_hash("password123"),
                role="admin"
            )

            db.session.add(user)
            db.session.commit()

            assert user.username == "testuser"
            assert user.role == "admin"
