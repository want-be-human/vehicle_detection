# -*- coding: utf-8 -*-
# ruff: noqa: E402
"""
测试配置文件 (conftest.py)

提供测试所需的通用fixtures和配置:
- Flask应用实例
- 测试客户端
- 数据库session
- Mock对象
"""

import sys
import os

# 添加项目根目录到path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest  # noqa: E402
from unittest.mock import Mock, patch  # noqa: E402
from datetime import datetime  # noqa: E402
from app.config.config import Config  # noqa: E402


class TestConfig(Config):
    """测试配置类"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test_secret_key'


@pytest.fixture(scope="session")  # type: ignore[misc]
def app():
    """创建测试应用实例 - 使用mock避免scheduler启动"""
    # 先导入模块以便patch能工作
    import app.config.scheduler_config
    
    # Mock scheduler以避免在测试中启动真实的调度器
    with patch.object(app.config.scheduler_config, 'scheduler') as mock_scheduler:
        mock_scheduler.start = Mock()
        mock_scheduler.shutdown = Mock()
        mock_scheduler.running = False
        mock_scheduler.add_job = Mock()
        
        from app import create_app
        
        _app = create_app(TestConfig)
        _app.config['TESTING'] = True
        _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        yield _app


@pytest.fixture(scope="function")
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope="function")
def app_context(app):
    """提供应用上下文"""
    with app.app_context():
        yield


@pytest.fixture(scope="function")
def db_session(app):
    """创建数据库session并在测试后清理"""
    from app import db
    
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def mock_socketio():
    """模拟SocketIO"""
    with patch('app.utils.websocket_utils.socketio') as mock:
        mock.emit = Mock()
        yield mock


@pytest.fixture
def sample_camera_data():
    """示例摄像头数据"""
    return {
        'name': 'Test Camera',
        'ip_address': '192.168.1.100',
        'port': 554,
        'url': 'rtsp://192.168.1.100:554/stream',
        'resolution': '1920x1080',
        'frame_rate': 30,
        'encoding_format': 'H.264',
        'restricted_areas': [
            {'id': 1, 'points': [[100, 100], [200, 100], [200, 200], [100, 200]]}
        ]
    }


@pytest.fixture
def sample_detection_data():
    """示例检测数据"""
    return {
        'camera_id': 1,
        'stream_url': 'rtsp://192.168.1.100:554/stream',
        'model_path': 'yolov8n.pt',
        'tracking_config': 'botsort.yaml',
        'save_dir': 'streams/1',
        'retention_days': 30
    }


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        'username': 'testuser',
        'password': 'TestPass123!',
        'role': 'user'
    }


@pytest.fixture
def mock_cv2():
    """模拟OpenCV"""
    with patch('cv2.VideoCapture') as mock_capture, \
         patch('cv2.VideoWriter') as mock_writer, \
         patch('cv2.imencode') as mock_encode, \
         patch('cv2.resize') as mock_resize:
        
        # 配置VideoCapture mock
        mock_cap_instance = Mock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.read.return_value = (True, Mock())
        mock_capture.return_value = mock_cap_instance
        
        # 配置VideoWriter mock
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance
        
        # 配置imencode mock
        mock_encode.return_value = (True, Mock(tobytes=Mock(return_value=b'fake_image')))
        
        yield {
            'capture': mock_capture,
            'writer': mock_writer,
            'encode': mock_encode,
            'resize': mock_resize
        }


@pytest.fixture
def mock_yolo():
    """模拟YOLO模型"""
    with patch('app.utils.yolo_integration.YOLO') as mock:
        mock_instance = Mock()
        mock_instance.track.return_value = iter([])
        mock_instance.to.return_value = mock_instance
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def sample_violation_data():
    """示例违规数据"""
    return {
        'camera_id': 1,
        'camera_name': 'Test Camera',
        'timestamp': datetime.now(),
        'vehicle_type': 'car',
        'location': '{"x": 150, "y": 150}',
        'violation_type': 'parking',
        'area_id': 1
    }


@pytest.fixture
def mock_detection_result():
    """模拟检测结果"""
    mock_result = Mock()
    mock_result.boxes = Mock()
    mock_result.boxes.xywh = Mock()
    mock_result.boxes.xywh.cpu.return_value = [[150, 150, 50, 30]]
    mock_result.boxes.id = Mock()
    mock_result.boxes.id.int.return_value.cpu.return_value.tolist.return_value = [1]
    mock_result.boxes.cls = Mock()
    mock_result.boxes.cls.cpu.return_value.tolist.return_value = [2]  # car
    mock_result.plot.return_value = Mock()
    return mock_result
