# -*- coding: utf-8 -*-
"""
模型测试 (test_models.py)

覆盖所有数据模型的测试:
- Camera模型
- Detection模型
- Violation模型
- User模型
- Statistics模型
"""

import pytest
from datetime import datetime, date


class TestCameraModel:
    """摄像头模型测试"""
    
    def test_camera_creation(self, db_session):
        """测试摄像头创建"""
        from app.models.camera import Camera
        
        camera = Camera(
            name='Test Camera',
            ip_address='192.168.1.100',
            port=554,
            url='rtsp://192.168.1.100:554/stream',
            resolution='1920x1080',
            frame_rate=30,
            encoding_format='H.264',
            model='yolov8n.pt',
            tracking_config='botsort.yaml',
            is_active=True,
            status='online',
            restricted_areas=[{'id': 1, 'points': [[0, 0], [100, 0], [100, 100], [0, 100]]}]
        )
        
        db_session.session.add(camera)
        db_session.session.commit()
        
        assert camera.id is not None
        assert camera.name == 'Test Camera'
        assert camera.ip_address == '192.168.1.100'
        assert camera.port == 554
        assert camera.status == 'online'
        assert camera.is_active is True
        assert len(camera.restricted_areas) == 1
    
    def test_camera_default_values(self, db_session):
        """测试摄像头默认值"""
        from app.models.camera import Camera
        
        camera = Camera(
            name='Minimal Camera',
            ip_address='10.0.0.1',
            port=8080,
            url='http://10.0.0.1:8080/stream'
        )
        
        db_session.session.add(camera)
        db_session.session.commit()
        
        assert camera.is_active is True
        assert camera.status == 'offline'
        assert camera.resolution is None
        assert camera.frame_rate is None
    
    def test_camera_repr(self, db_session):
        """测试摄像头__repr__方法"""
        from app.models.camera import Camera
        
        camera = Camera(
            name='Repr Camera',
            ip_address='172.16.0.1',
            port=554,
            url='rtsp://172.16.0.1:554/stream'
        )
        
        repr_str = repr(camera)
        assert 'Repr Camera' in repr_str
        assert '172.16.0.1' in repr_str
    
    def test_camera_with_detections(self, db_session):
        """测试摄像头与检测记录的关联"""
        from app.models.camera import Camera
        from app.models.detection import Detection
        
        camera = Camera(
            name='Camera with Detections',
            ip_address='192.168.1.200',
            port=554,
            url='rtsp://192.168.1.200:554/stream'
        )
        db_session.session.add(camera)
        db_session.session.commit()
        
        detection = Detection(
            camera_id=camera.id,
            timestamp=datetime.now(),
            video_path='/path/to/video.mp4'
        )
        db_session.session.add(detection)
        db_session.session.commit()
        
        assert len(camera.detections) == 1  # type: ignore[arg-type]
        assert camera.detections[0].video_path == '/path/to/video.mp4'  # type: ignore[index]


class TestDetectionModel:
    """检测记录模型测试"""
    
    def test_detection_creation(self, db_session):
        """测试检测记录创建"""
        from app.models.camera import Camera
        from app.models.detection import Detection
        
        # 先创建摄像头
        camera = Camera(
            name='Test Camera',
            ip_address='192.168.1.100',
            port=554,
            url='rtsp://test'
        )
        db_session.session.add(camera)
        db_session.session.commit()
        
        detection = Detection(
            camera_id=camera.id,
            timestamp=datetime.now(),
            video_path='/path/video.mp4',
            vehicle_type='car',
            location='Gate 1',
            is_violation=True
        )
        db_session.session.add(detection)
        db_session.session.commit()
        
        assert detection.id is not None
        assert detection.camera_id == camera.id
        assert detection.vehicle_type == 'car'
        assert detection.is_violation is True
    
    def test_detection_default_values(self, db_session):
        """测试检测记录默认值"""
        from app.models.camera import Camera
        from app.models.detection import Detection
        
        camera = Camera(
            name='Test Camera',
            ip_address='192.168.1.100',
            port=554,
            url='rtsp://test'
        )
        db_session.session.add(camera)
        db_session.session.commit()
        
        detection = Detection(
            camera_id=camera.id,
            timestamp=datetime.now()
        )
        db_session.session.add(detection)
        db_session.session.commit()
        
        assert detection.is_violation is False
        assert detection.vehicle_type is None
        assert detection.video_path is None
    
    def test_detection_repr(self, db_session):
        """测试检测记录__repr__方法"""
        from app.models.camera import Camera
        from app.models.detection import Detection
        
        camera = Camera(
            name='Test Camera',
            ip_address='192.168.1.100',
            port=554,
            url='rtsp://test'
        )
        db_session.session.add(camera)
        db_session.session.commit()
        
        detection = Detection(
            camera_id=camera.id,
            timestamp=datetime.now(),
            vehicle_type='truck'
        )
        
        repr_str = repr(detection)
        assert 'truck' in repr_str


class TestViolationModel:
    """违规记录模型测试"""
    
    def test_violation_creation(self, db_session):
        """测试违规记录创建"""
        from app.models.camera import Camera
        from app.models.violation import Violation
        
        camera = Camera(
            name='Test Camera',
            ip_address='192.168.1.100',
            port=554,
            url='rtsp://test'
        )
        db_session.session.add(camera)
        db_session.session.commit()
        
        violation = Violation(
            camera_id=camera.id,
            camera_name='Test Camera',
            timestamp=datetime.now(),
            vehicle_type='car',
            location='{"x": 100, "y": 200}',
            violation_type='parking',
            area_id=1
        )
        db_session.session.add(violation)
        db_session.session.commit()
        
        assert violation.id is not None
        assert violation.camera_id == camera.id
        assert violation.violation_type == 'parking'
    
    def test_violation_to_dict(self, db_session):
        """测试违规记录to_dict方法"""
        from app.models.camera import Camera
        from app.models.violation import Violation
        
        camera = Camera(
            name='Test Camera',
            ip_address='192.168.1.100',
            port=554,
            url='rtsp://test'
        )
        db_session.session.add(camera)
        db_session.session.commit()
        
        now = datetime.now()
        violation = Violation(
            camera_id=camera.id,
            camera_name='Test Camera',
            timestamp=now,
            vehicle_type='bus',
            location='{"x": 300, "y": 400}',
            violation_type='parking',
            area_id=2
        )
        db_session.session.add(violation)
        db_session.session.commit()
        
        violation_dict = violation.to_dict()
        
        assert violation_dict['camera_id'] == camera.id
        assert violation_dict['camera_name'] == 'Test Camera'
        assert violation_dict['vehicle_type'] == 'bus'
        assert violation_dict['violation_type'] == 'parking'
        assert violation_dict['area_id'] == 2
        assert 'timestamp' in violation_dict
    
    def test_violation_default_type(self, db_session):
        """测试违规记录默认类型"""
        from app.models.camera import Camera
        from app.models.violation import Violation
        
        camera = Camera(
            name='Test Camera',
            ip_address='192.168.1.100',
            port=554,
            url='rtsp://test'
        )
        db_session.session.add(camera)
        db_session.session.commit()
        
        violation = Violation(
            camera_id=camera.id,
            camera_name='Test Camera',
            timestamp=datetime.now(),
            vehicle_type='car',
            location='{"x": 100, "y": 100}'
        )
        db_session.session.add(violation)
        db_session.session.commit()
        
        assert violation.violation_type == 'parking'


class TestUserModel:
    """用户模型测试"""
    
    def test_user_creation(self, db_session):
        """测试用户创建"""
        from app.models.user import User
        
        user = User(
            username='testuser',
            password='hashed_password',
            role='admin',
            phone='13800138000'
        )
        db_session.session.add(user)
        db_session.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.role == 'admin'
        assert user.phone == '13800138000'
    
    def test_user_default_role(self, db_session):
        """测试用户默认角色"""
        from app.models.user import User
        
        user = User(
            username='normaluser',
            password='hashed_password'
        )
        db_session.session.add(user)
        db_session.session.commit()
        
        assert user.role == 'user'
        assert user.phone is None
    
    def test_user_unique_username(self, db_session):
        """测试用户名唯一性"""
        from app.models.user import User
        from sqlalchemy.exc import IntegrityError
        
        user1 = User(username='unique_user', password='pass1')
        db_session.session.add(user1)
        db_session.session.commit()
        
        user2 = User(username='unique_user', password='pass2')
        db_session.session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.session.commit()
        
        db_session.session.rollback()


class TestStatisticsModel:
    """统计模型测试"""
    
    def test_statistics_creation(self, db_session):
        """测试统计记录创建"""
        from app.models.statistics import StatisticsModel
        
        stats = StatisticsModel(
            date=date.today(),
            peak_hours=[{'hour': 8, 'count': 100}, {'hour': 17, 'count': 120}],
            vehicle_distribution={'car': 500, 'bus': 50, 'truck': 30},
            hourly_flow=[{'hour': i, 'count': 10 + i * 5} for i in range(24)],
            total_count=580,
            chart_data={'pie': 'data', 'line': 'data'}
        )
        db_session.session.add(stats)
        db_session.session.commit()
        
        assert stats.id is not None
        assert stats.total_count == 580
        assert len(stats.peak_hours) == 2
    
    def test_statistics_to_dict(self, db_session):
        """测试统计记录to_dict方法"""
        from app.models.statistics import StatisticsModel
        
        today = date.today()
        stats = StatisticsModel(
            date=today,
            peak_hours=[{'hour': 9, 'count': 150}],
            vehicle_distribution={'car': 200},
            hourly_flow=[{'hour': 9, 'count': 150}],
            total_count=200
        )
        db_session.session.add(stats)
        db_session.session.commit()
        
        stats_dict = stats.to_dict()
        
        assert stats_dict['date'] == today.strftime('%Y-%m-%d')
        assert stats_dict['total_count'] == 200
        assert stats_dict['vehicle_distribution'] == {'car': 200}
    
    def test_statistics_repr(self, db_session):
        """测试统计记录__repr__方法"""
        from app.models.statistics import StatisticsModel
        
        stats = StatisticsModel(
            date=date(2024, 3, 15),
            total_count=100
        )
        
        repr_str = repr(stats)
        assert '2024-03-15' in repr_str
    
    def test_statistics_default_values(self, db_session):
        """测试统计记录默认值"""
        from app.models.statistics import StatisticsModel
        
        stats = StatisticsModel(date=date.today())
        db_session.session.add(stats)
        db_session.session.commit()
        
        assert stats.total_count == 0
        assert stats.peak_hours is None
        assert stats.vehicle_distribution is None
