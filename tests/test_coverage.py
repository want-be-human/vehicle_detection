from unittest.mock import patch

import pytest

from app import db
from app.services.camera_service import CameraService
from app.services.violation_service import ViolationService

try:
    from app.services.detection_service import DetectionService
    DETECTION_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - optional dependency guard
    DetectionService = None
    DETECTION_IMPORT_ERROR = exc


class TestCoverage:
    def test_full_coverage_paths(self, app):
        if DetectionService is None:
            pytest.skip(f"DetectionService unavailable: {DETECTION_IMPORT_ERROR}")

        with app.app_context():
            db.create_all()

            test_camera_data = {
                'name': '覆盖率测试摄像头',
                'ip_address': '192.168.1.200',
                'port': 554,
                'url': 'rtsp://test/stream',
                'resolution': '1280x720',
                'frame_rate': 25,
                'encoding_format': 'H.265'
            }

            with patch('cv2.VideoCapture'):
                CameraService.validate_camera_data(test_camera_data)

                status = DetectionService.get_processing_status()
                assert isinstance(status, dict)

                violation_service = ViolationService()
                violations = violation_service.get_violations({'camera_id': 1})
                assert isinstance(violations, list)

    def test_error_handling_paths(self):
        invalid_data = {'name': '测试'}

        with pytest.raises(ValueError):
            CameraService.validate_camera_data(invalid_data)

        violation_service = ViolationService()
        assert violation_service.get_violations(None) == []
