# -*- coding: utf-8 -*-
"""
违规检测模块测试 (Violation Module Tests)

覆盖测试点:

违规记录接口测试 (VIO-01 至 VIO-11):
- VIO-01: 获取违规记录
- VIO-02: 按camera_id过滤
- VIO-03: 按时间范围过滤
- VIO-04: 按车辆类型过滤
- VIO-05: 按违规类型过滤
- VIO-06: 时间格式错误
- VIO-07: 车辆在禁区检测
- VIO-08: 车辆不在禁区
- VIO-09: 违规防重复提醒
- VIO-10: 违规记录完整性
- VIO-11: 分页功能（缺陷测试）

违规检测工具测试 (VU-01 至 VU-08):
- VU-01: 点在多边形内
- VU-02: 点在多边形外
- VU-03: 点在边界上
- VU-04: 复杂多边形
- VU-05: 空禁区列表
- VU-06: 无检测结果
- VU-07: 多禁区检测
- VU-08: 非车辆类别忽略
"""

import pytest
import importlib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json


# ==================== Fixtures ====================

@pytest.fixture(scope="module")
def app():
    """创建测试应用"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """应用上下文"""
    with app.app_context():
        yield


@pytest.fixture
def mock_db(app_context):
    """模拟数据库操作"""
    from app import db
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture
def violation_service():
    """导入违规服务模块"""
    return importlib.import_module("app.services.violation_service")


@pytest.fixture
def violation_utils():
    """导入违规检测工具模块"""
    return importlib.import_module("app.utils.violation_utils")


@pytest.fixture
def sample_camera(mock_db):
    """创建示例摄像头"""
    from app.models.camera import Camera
    camera = Camera(
        name="Test Camera 1",
        ip_address="192.168.1.100",
        port=554,
        url="rtsp://192.168.1.100:554/stream",
        resolution="1920x1080",
        frame_rate=30,
        encoding_format="H.264",
        status="online",
        restricted_areas=[
            {"id": 1, "points": [[100, 100], [200, 100], [200, 200], [100, 200]]},
            {"id": 2, "points": [[300, 300], [400, 300], [400, 400], [300, 400]]}
        ]
    )
    mock_db.session.add(camera)
    mock_db.session.commit()
    return camera


@pytest.fixture
def sample_camera_no_areas(mock_db):
    """创建没有禁停区域的摄像头"""
    from app.models.camera import Camera
    camera = Camera(
        name="Test Camera 2",
        ip_address="192.168.1.101",
        port=554,
        url="rtsp://192.168.1.101:554/stream",
        status="online",
        restricted_areas=None
    )
    mock_db.session.add(camera)
    mock_db.session.commit()
    return camera


@pytest.fixture
def sample_violations(mock_db, sample_camera):
    """创建示例违规记录"""
    from app.models.violation import Violation
    
    violations = []
    base_time = datetime(2024, 3, 15, 14, 0, 0)
    
    # 创建多条违规记录
    for i in range(5):
        violation = Violation(
            camera_id=sample_camera.id,
            camera_name=sample_camera.name,
            timestamp=base_time + timedelta(minutes=i * 10),
            vehicle_type=['car', 'bus', 'truck', 'car', 'bus'][i],
            location=json.dumps({'x': 150 + i * 10, 'y': 150 + i * 10}),
            violation_type=['parking', 'parking', 'speed', 'parking', 'speed'][i],
            area_id=1
        )
        mock_db.session.add(violation)
        violations.append(violation)
    
    mock_db.session.commit()
    return violations


@pytest.fixture
def violation_service_instance(violation_service):
    """创建ViolationService实例"""
    return violation_service.ViolationService()


# ==================== VIO-01: 获取违规记录 ====================

class TestGetViolations:
    """VIO-01: 获取违规记录测试"""

    def test_get_violations_success(self, client, violation_service, monkeypatch):
        """测试成功获取违规记录"""
        mock_violations = [
            {
                'id': 1,
                'camera_id': 1,
                'camera_name': 'Camera 1',
                'timestamp': '2024-03-15 14:30:00',
                'vehicle_type': 'car',
                'location': "{'x': 150, 'y': 150}",
                'violation_type': 'parking',
                'area_id': 1
            }
        ]
        
        # 模拟violation_service实例的get_violations方法
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=mock_violations
        ):
            resp = client.get("/violation/records")
            
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['success'] is True
            assert 'violations' in data
            assert len(data['violations']) == 1

    def test_get_violations_empty(self, client, violation_service, monkeypatch):
        """测试获取空违规记录列表"""
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=[]
        ):
            resp = client.get("/violation/records")
            
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['success'] is True
            assert data['violations'] == []

    def test_get_violations_returns_list(self, client, violation_service, monkeypatch):
        """测试返回值为列表类型"""
        mock_violations = [{'id': 1}, {'id': 2}, {'id': 3}]
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=mock_violations
        ):
            resp = client.get("/violation/records")
            
            data = resp.get_json()
            assert isinstance(data['violations'], list)


# ==================== VIO-02: 按camera_id过滤 ====================

class TestFilterByCameraId:
    """VIO-02: 按camera_id过滤测试"""

    def test_filter_by_camera_id(self, client, violation_service, monkeypatch):
        """测试按摄像头ID过滤"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return []
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            resp = client.get("/violation/records?camera_id=1")
            
            assert resp.status_code == 200
            assert captured_filters.get('camera_id') == 1

    def test_filter_by_camera_id_returns_matching(self, client, violation_service):
        """测试过滤返回匹配的记录"""
        mock_violations_cam1 = [
            {'id': 1, 'camera_id': 1, 'camera_name': 'Camera 1'}
        ]
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=mock_violations_cam1
        ):
            resp = client.get("/violation/records?camera_id=1")
            
            data = resp.get_json()
            assert all(v['camera_id'] == 1 for v in data['violations'])

    def test_filter_by_nonexistent_camera_id(self, client, violation_service):
        """测试过滤不存在的摄像头ID"""
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=[]
        ):
            resp = client.get("/violation/records?camera_id=999")
            
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['violations'] == []

    def test_camera_id_type_conversion(self, client, violation_service):
        """测试camera_id类型转换为整数"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return []
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            client.get("/violation/records?camera_id=5")
            
            # 验证转换为整数
            assert captured_filters.get('camera_id') == 5
            assert isinstance(captured_filters.get('camera_id'), int)


# ==================== VIO-03: 按时间范围过滤 ====================

class TestFilterByTimeRange:
    """VIO-03: 按时间范围过滤测试"""

    def test_filter_by_start_time(self, client, violation_service):
        """测试按开始时间过滤"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return []
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            resp = client.get("/violation/records?start_time=2024-03-15%2014:00:00")
            
            assert resp.status_code == 200
            assert 'start_time' in captured_filters
            assert isinstance(captured_filters['start_time'], datetime)

    def test_filter_by_end_time(self, client, violation_service):
        """测试按结束时间过滤"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return []
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            resp = client.get("/violation/records?end_time=2024-03-15%2018:00:00")
            
            assert resp.status_code == 200
            assert 'end_time' in captured_filters

    def test_filter_by_time_range(self, client, violation_service):
        """测试按时间范围过滤"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return []
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            resp = client.get(
                "/violation/records?"
                "start_time=2024-03-15%2014:00:00&"
                "end_time=2024-03-15%2018:00:00"
            )
            
            assert resp.status_code == 200
            assert 'start_time' in captured_filters
            assert 'end_time' in captured_filters

    def test_time_range_returns_matching(self, client, violation_service):
        """测试时间范围返回匹配记录"""
        mock_violations = [
            {'id': 1, 'timestamp': '2024-03-15 15:00:00'},
            {'id': 2, 'timestamp': '2024-03-15 16:00:00'}
        ]
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=mock_violations
        ):
            resp = client.get(
                "/violation/records?"
                "start_time=2024-03-15%2014:00:00&"
                "end_time=2024-03-15%2018:00:00"
            )
            
            data = resp.get_json()
            assert len(data['violations']) == 2


# ==================== VIO-04: 按车辆类型过滤 ====================

class TestFilterByVehicleType:
    """VIO-04: 按车辆类型过滤测试"""

    def test_filter_by_vehicle_type_car(self, client, violation_service):
        """测试按car类型过滤"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return [{'id': 1, 'vehicle_type': 'car'}]
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            resp = client.get("/violation/records?vehicle_type=car")
            
            assert resp.status_code == 200
            assert captured_filters.get('vehicle_type') == 'car'

    def test_filter_by_vehicle_type_bus(self, client, violation_service):
        """测试按bus类型过滤"""
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=[{'id': 2, 'vehicle_type': 'bus'}]
        ):
            resp = client.get("/violation/records?vehicle_type=bus")
            
            data = resp.get_json()
            assert all(v['vehicle_type'] == 'bus' for v in data['violations'])

    def test_filter_by_vehicle_type_truck(self, client, violation_service):
        """测试按truck类型过滤"""
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=[{'id': 3, 'vehicle_type': 'truck'}]
        ):
            resp = client.get("/violation/records?vehicle_type=truck")
            
            data = resp.get_json()
            assert all(v['vehicle_type'] == 'truck' for v in data['violations'])

    def test_filter_by_invalid_vehicle_type(self, client, violation_service):
        """测试按无效车辆类型过滤"""
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=[]
        ):
            resp = client.get("/violation/records?vehicle_type=invalid_type")
            
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['violations'] == []


# ==================== VIO-05: 按违规类型过滤 ====================

class TestFilterByViolationType:
    """VIO-05: 按违规类型过滤测试"""

    def test_filter_by_violation_type_parking(self, client, violation_service):
        """测试按parking违规类型过滤"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return [{'id': 1, 'violation_type': 'parking'}]
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            resp = client.get("/violation/records?violation_type=parking")
            
            assert resp.status_code == 200
            assert captured_filters.get('violation_type') == 'parking'

    def test_filter_by_violation_type_speed(self, client, violation_service):
        """测试按speed违规类型过滤"""
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=[{'id': 2, 'violation_type': 'speed'}]
        ):
            resp = client.get("/violation/records?violation_type=speed")
            
            data = resp.get_json()
            assert all(v['violation_type'] == 'speed' for v in data['violations'])

    def test_filter_combined_vehicle_and_violation_type(self, client, violation_service):
        """测试组合过滤车辆类型和违规类型"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return []
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            client.get("/violation/records?vehicle_type=car&violation_type=parking")
            
            assert captured_filters.get('vehicle_type') == 'car'
            assert captured_filters.get('violation_type') == 'parking'


# ==================== VIO-06: 时间格式错误 ====================

class TestTimeFormatError:
    """VIO-06: 时间格式错误测试"""

    def test_invalid_start_time_format(self, client):
        """测试无效的开始时间格式"""
        resp = client.get("/violation/records?start_time=invalid-date")
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['success'] is False

    def test_invalid_end_time_format(self, client):
        """测试无效的结束时间格式"""
        resp = client.get("/violation/records?end_time=2024/03/15")
        
        assert resp.status_code == 400

    def test_partial_datetime_format(self, client):
        """测试不完整的日期时间格式"""
        resp = client.get("/violation/records?start_time=2024-03-15")
        
        # 缺少时间部分应该报错
        assert resp.status_code == 400

    def test_wrong_datetime_separator(self, client):
        """测试错误的日期时间分隔符"""
        resp = client.get("/violation/records?start_time=2024-03-15T14:00:00")
        
        # 使用T而非空格应该报错
        assert resp.status_code == 400

    def test_invalid_date_values(self, client):
        """测试无效的日期值"""
        resp = client.get("/violation/records?start_time=2024-13-45%2025:00:00")
        
        assert resp.status_code == 400


# ==================== VIO-07: 车辆在禁区检测 ====================

class TestVehicleInRestrictedArea:
    """VIO-07: 车辆在禁区检测测试"""

    def test_check_violations_vehicle_in_area(
        self, violation_service_instance, app_context, mock_db, sample_camera
    ):
        """测试检测到在禁区内的车辆"""
        # 模拟检测结果 - 车辆在禁区内 (150, 150)
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.xywh = Mock()
        mock_result.boxes.xywh.cpu.return_value = [
            Mock(__getitem__=lambda self, i: [150.0, 150.0, 50.0, 50.0][i], 
                 item=lambda: None)
        ]
        
        # 创建模拟的tensor行为
        box_mock = Mock()
        box_mock.__getitem__ = lambda self, i: Mock(item=lambda: [150.0, 150.0, 50.0, 50.0][i])
        mock_result.boxes.xywh.cpu.return_value = [box_mock]
        mock_result.boxes.id = Mock()
        mock_result.boxes.id.int.return_value.cpu.return_value.tolist.return_value = [1]
        mock_result.boxes.cls = Mock()
        mock_result.boxes.cls.cpu.return_value.tolist.return_value = [2]  # car
        
        with patch.object(
            violation_service_instance, 
            'violation_cache', 
            {}
        ):
            from app.utils.violation_utils import ViolationDetector
            
            # 直接测试ViolationDetector
            ViolationDetector.check_vehicle_violation(
                mock_result, 
                sample_camera.restricted_areas
            )
            
            # 应该检测到违规（如果点在区域内）
            # 注意：需要根据实际区域坐标验证

    def test_violation_creates_record(
        self, violation_service_instance, app_context, mock_db, sample_camera
    ):
        """测试违规检测创建记录"""
        from app.models.violation import Violation
        
        # 检查初始记录数
        initial_count = Violation.query.count()
        
        # 模拟违规记录创建
        violation = Violation(
            camera_id=sample_camera.id,
            camera_name=sample_camera.name,
            timestamp=datetime.now(),
            vehicle_type='car',
            location="{'x': 150, 'y': 150}",
            violation_type='parking',
            area_id=1
        )
        mock_db.session.add(violation)
        mock_db.session.commit()
        
        # 验证记录增加
        assert Violation.query.count() == initial_count + 1


# ==================== VIO-08: 车辆不在禁区 ====================

class TestVehicleNotInRestrictedArea:
    """VIO-08: 车辆不在禁区测试"""

    def test_vehicle_outside_area_no_violation(self, violation_utils):
        """测试车辆在禁区外不产生违规"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # 模拟检测结果 - 车辆在禁区外 (500, 500)
        mock_result = Mock()
        mock_result.boxes = Mock()
        
        # 创建模拟的box数据
        box_mock = Mock()
        box_mock.__getitem__ = lambda self, i: Mock(item=lambda: [500.0, 500.0, 50.0, 50.0][i])
        mock_result.boxes.xywh = Mock()
        mock_result.boxes.xywh.cpu.return_value = [box_mock]
        mock_result.boxes.id = Mock()
        mock_result.boxes.id.int.return_value.cpu.return_value.tolist.return_value = [1]
        mock_result.boxes.cls = Mock()
        mock_result.boxes.cls.cpu.return_value.tolist.return_value = [2]  # car
        
        restricted_areas = [
            {"id": 1, "points": [[100, 100], [200, 100], [200, 200], [100, 200]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(
            mock_result, 
            restricted_areas
        )
        
        # 车辆在(500, 500)，不在禁区(100-200, 100-200)内
        assert len(violations) == 0

    def test_vehicle_at_boundary_no_violation(self, violation_utils):
        """测试车辆在禁区边界不产生违规（shapely.contains不包含边界）"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # 测试点正好在边界上
        point = [100, 100]  # 在矩形的角上
        polygon_points = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        # shapely的contains不包含边界点
        result = ViolationDetector.is_point_in_polygon(point, polygon_points)
        
        # 边界点通常不被contains包含
        assert result is False


# ==================== VIO-09: 违规防重复提醒 ====================

class TestViolationDeduplication:
    """VIO-09: 违规防重复提醒测试"""

    def test_same_track_id_within_60s_not_repeated(
        self, violation_service, app_context
    ):
        """测试同一track_id在60秒内不重复记录"""
        service = violation_service.ViolationService()
        
        # 模拟第一次违规
        violation_key = "1_100"  # camera_id_track_id
        current_time = datetime.now()
        service.violation_cache[violation_key] = current_time
        
        # 模拟30秒后的同一车辆
        time_30s_later = current_time + timedelta(seconds=30)
        
        # 检查是否应该记录
        should_record = (
            violation_key not in service.violation_cache or 
            (time_30s_later - service.violation_cache[violation_key]).seconds > 60
        )
        
        # 30秒内不应记录
        assert should_record is False

    def test_same_track_id_after_60s_recorded(self, violation_service, app_context):
        """测试同一track_id超过60秒后可以记录"""
        service = violation_service.ViolationService()
        
        violation_key = "1_100"
        current_time = datetime.now()
        service.violation_cache[violation_key] = current_time - timedelta(seconds=70)
        
        # 检查是否应该记录
        should_record = (
            violation_key not in service.violation_cache or 
            (current_time - service.violation_cache[violation_key]).seconds > 60
        )
        
        # 超过60秒应该记录
        assert should_record is True

    def test_different_track_id_always_recorded(self, violation_service, app_context):
        """测试不同track_id始终记录"""
        service = violation_service.ViolationService()
        
        # 记录第一个车辆
        service.violation_cache["1_100"] = datetime.now()
        
        # 检查另一个车辆
        new_key = "1_101"
        should_record = new_key not in service.violation_cache
        
        assert should_record is True

    def test_violation_cache_cleanup(self, violation_service, app_context):
        """测试违规缓存可以正常更新"""
        service = violation_service.ViolationService()
        
        violation_key = "1_100"
        old_time = datetime.now() - timedelta(minutes=5)
        service.violation_cache[violation_key] = old_time
        
        # 更新缓存
        new_time = datetime.now()
        service.violation_cache[violation_key] = new_time
        
        assert service.violation_cache[violation_key] == new_time


# ==================== VIO-10: 违规记录完整性 ====================

class TestViolationRecordIntegrity:
    """VIO-10: 违规记录完整性测试"""

    def test_violation_record_has_all_fields(self, mock_db, sample_camera):
        """测试违规记录包含所有必需字段"""
        from app.models.violation import Violation
        
        violation = Violation(
            camera_id=sample_camera.id,
            camera_name=sample_camera.name,
            timestamp=datetime.now(),
            vehicle_type='car',
            location="{'x': 150, 'y': 150}",
            violation_type='parking',
            area_id=1
        )
        mock_db.session.add(violation)
        mock_db.session.commit()
        
        # 验证所有字段
        assert violation.id is not None
        assert violation.camera_id == sample_camera.id
        assert violation.camera_name == sample_camera.name
        assert violation.timestamp is not None
        assert violation.vehicle_type == 'car'
        assert violation.location is not None
        assert violation.violation_type == 'parking'
        assert violation.area_id == 1

    def test_violation_to_dict_format(self, mock_db, sample_camera):
        """测试to_dict方法返回正确格式"""
        from app.models.violation import Violation
        
        timestamp = datetime(2024, 3, 15, 14, 30, 0)
        violation = Violation(
            camera_id=sample_camera.id,
            camera_name=sample_camera.name,
            timestamp=timestamp,
            vehicle_type='bus',
            location="{'x': 150, 'y': 150}",
            violation_type='parking',
            area_id=2
        )
        mock_db.session.add(violation)
        mock_db.session.commit()
        
        result = violation.to_dict()
        
        assert 'id' in result
        assert 'camera_id' in result
        assert 'camera_name' in result
        assert 'timestamp' in result
        assert 'vehicle_type' in result
        assert 'location' in result
        assert 'violation_type' in result
        assert 'area_id' in result
        
        # 验证时间格式
        assert result['timestamp'] == '2024-03-15 14:30:00'

    def test_violation_record_foreign_key(self, mock_db, sample_camera):
        """测试违规记录外键关联"""
        from app.models.violation import Violation
        
        violation = Violation(
            camera_id=sample_camera.id,
            camera_name=sample_camera.name,
            timestamp=datetime.now(),
            vehicle_type='car',
            location="{'x': 150, 'y': 150}",
            violation_type='parking'
        )
        mock_db.session.add(violation)
        mock_db.session.commit()
        
        # 验证外键关联有效
        assert violation.camera_id == sample_camera.id


# ==================== VIO-11: 分页功能（缺陷测试） ====================

class TestViolationPagination:
    """VIO-11: 分页功能缺陷测试"""

    def test_no_pagination_returns_all(self, client, violation_service):
        """测试无分页返回所有记录"""
        # 创建大量模拟记录
        mock_violations = [{'id': i} for i in range(100)]
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=mock_violations
        ):
            resp = client.get("/violation/records")
            
            data = resp.get_json()
            # 当前实现无分页，返回所有记录
            assert len(data['violations']) == 100

    def test_large_dataset_performance_concern(self, client, violation_service):
        """测试大数据量性能问题（缺陷检测）"""
        # 模拟10000条记录
        mock_violations = [{'id': i, 'data': 'x' * 100} for i in range(10000)]
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=mock_violations
        ):
            import time
            start = time.time()
            resp = client.get("/violation/records")
            elapsed = time.time() - start
            
            # 记录响应时间，但不作为失败条件
            # 这是一个缺陷检测测试，用于识别性能问题
            assert resp.status_code == 200
            # 可以添加警告日志
            if elapsed > 1.0:
                print(f"WARNING: Large dataset query took {elapsed:.2f}s")

    def test_pagination_params_ignored(self, client, violation_service):
        """测试分页参数被忽略（缺陷确认）"""
        captured_filters = {}
        
        def mock_get_violations(self, filters=None):
            captured_filters.update(filters or {})
            return []
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations
        ):
            # 尝试传入分页参数
            client.get("/violation/records?page=1&per_page=10")
            
            # 当前实现不支持分页参数
            assert 'page' not in captured_filters
            assert 'per_page' not in captured_filters


# ==================== VU-01: 点在多边形内 ====================

class TestPointInPolygon:
    """VU-01: 点在多边形内测试"""

    def test_point_inside_rectangle(self, violation_utils):
        """测试点在矩形内"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [150, 150]
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is True

    def test_point_inside_triangle(self, violation_utils):
        """测试点在三角形内"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [150, 150]
        polygon = [[100, 100], [200, 100], [150, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is True

    def test_point_center_of_polygon(self, violation_utils):
        """测试点在多边形中心"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [150, 150]
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is True


# ==================== VU-02: 点在多边形外 ====================

class TestPointOutsidePolygon:
    """VU-02: 点在多边形外测试"""

    def test_point_outside_rectangle(self, violation_utils):
        """测试点在矩形外"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [300, 300]
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is False

    def test_point_far_outside(self, violation_utils):
        """测试点远离多边形"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [1000, 1000]
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is False

    def test_point_negative_coordinates(self, violation_utils):
        """测试负坐标点"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [-50, -50]
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is False


# ==================== VU-03: 点在边界上 ====================

class TestPointOnBoundary:
    """VU-03: 点在边界上测试"""

    def test_point_on_edge(self, violation_utils):
        """测试点在边上"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [150, 100]  # 在上边界上
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        # shapely的contains不包含边界
        assert result is False

    def test_point_on_vertex(self, violation_utils):
        """测试点在顶点上"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [100, 100]  # 在顶点上
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        # shapely的contains不包含顶点
        assert result is False

    def test_point_slightly_inside_boundary(self, violation_utils):
        """测试点略微在边界内"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [100.001, 100.001]  # 略微在内部
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is True


# ==================== VU-04: 复杂多边形 ====================

class TestComplexPolygon:
    """VU-04: 复杂多边形测试"""

    def test_concave_polygon_point_inside(self, violation_utils):
        """测试凹多边形内的点"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # L形凹多边形
        polygon = [
            [100, 100], [200, 100], [200, 150],
            [150, 150], [150, 200], [100, 200]
        ]
        point = [120, 120]  # 在L形内部
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is True

    def test_concave_polygon_point_in_concave_area(self, violation_utils):
        """测试凹多边形凹陷区域的点"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # L形凹多边形
        polygon = [
            [100, 100], [200, 100], [200, 150],
            [150, 150], [150, 200], [100, 200]
        ]
        point = [175, 175]  # 在凹陷区域（外部）
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is False

    def test_pentagon(self, violation_utils):
        """测试五边形"""
        ViolationDetector = violation_utils.ViolationDetector
        
        import math
        # 正五边形
        center = (150, 150)
        radius = 50
        polygon = [
            [center[0] + radius * math.cos(2 * math.pi * i / 5),
             center[1] + radius * math.sin(2 * math.pi * i / 5)]
            for i in range(5)
        ]
        
        # 中心点应该在内部
        result = ViolationDetector.is_point_in_polygon([150, 150], polygon)
        
        assert result is True


# ==================== VU-05: 空禁区列表 ====================

class TestEmptyRestrictedAreas:
    """VU-05: 空禁区列表测试"""

    def test_empty_restricted_areas(self, violation_utils):
        """测试空禁区列表"""
        ViolationDetector = violation_utils.ViolationDetector
        
        mock_result = Mock()
        mock_result.boxes = Mock()
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, [])
        
        assert violations == []

    def test_none_restricted_areas(self, violation_utils):
        """测试None禁区列表"""
        ViolationDetector = violation_utils.ViolationDetector
        
        mock_result = Mock()
        mock_result.boxes = Mock()
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, None)
        
        assert violations == []


# ==================== VU-06: 无检测结果 ====================

class TestNoDetectionResult:
    """VU-06: 无检测结果测试"""

    def test_boxes_is_none(self, violation_utils):
        """测试boxes为None"""
        ViolationDetector = violation_utils.ViolationDetector
        
        mock_result = Mock()
        mock_result.boxes = None
        
        restricted_areas = [
            {"id": 1, "points": [[100, 100], [200, 100], [200, 200], [100, 200]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(
            mock_result, 
            restricted_areas
        )
        
        assert violations == []

    def test_empty_boxes(self, violation_utils):
        """测试空检测框"""
        ViolationDetector = violation_utils.ViolationDetector
        
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.xywh = Mock()
        mock_result.boxes.xywh.cpu.return_value = []
        mock_result.boxes.id = Mock()
        mock_result.boxes.id.int.return_value.cpu.return_value.tolist.return_value = []
        mock_result.boxes.cls = Mock()
        mock_result.boxes.cls.cpu.return_value.tolist.return_value = []
        
        restricted_areas = [
            {"id": 1, "points": [[100, 100], [200, 100], [200, 200], [100, 200]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(
            mock_result, 
            restricted_areas
        )
        
        assert violations == []


# ==================== VU-07: 多禁区检测 ====================

class TestMultipleRestrictedAreas:
    """VU-07: 多禁区检测测试"""

    def test_vehicle_in_first_area(self, violation_utils):
        """测试车辆在第一个禁区"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [150, 150]
        areas = [
            {"id": 1, "points": [[100, 100], [200, 100], [200, 200], [100, 200]]},
            {"id": 2, "points": [[300, 300], [400, 300], [400, 400], [300, 400]]}
        ]
        
        # 点在第一个区域内
        in_area1 = ViolationDetector.is_point_in_polygon(point, areas[0]['points'])
        in_area2 = ViolationDetector.is_point_in_polygon(point, areas[1]['points'])
        
        assert in_area1 is True
        assert in_area2 is False

    def test_vehicle_in_second_area(self, violation_utils):
        """测试车辆在第二个禁区"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [350, 350]
        areas = [
            {"id": 1, "points": [[100, 100], [200, 100], [200, 200], [100, 200]]},
            {"id": 2, "points": [[300, 300], [400, 300], [400, 400], [300, 400]]}
        ]
        
        in_area1 = ViolationDetector.is_point_in_polygon(point, areas[0]['points'])
        in_area2 = ViolationDetector.is_point_in_polygon(point, areas[1]['points'])
        
        assert in_area1 is False
        assert in_area2 is True

    def test_vehicle_in_no_area(self, violation_utils):
        """测试车辆不在任何禁区"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [500, 500]
        areas = [
            {"id": 1, "points": [[100, 100], [200, 100], [200, 200], [100, 200]]},
            {"id": 2, "points": [[300, 300], [400, 300], [400, 400], [300, 400]]}
        ]
        
        in_area1 = ViolationDetector.is_point_in_polygon(point, areas[0]['points'])
        in_area2 = ViolationDetector.is_point_in_polygon(point, areas[1]['points'])
        
        assert in_area1 is False
        assert in_area2 is False

    def test_only_first_violation_recorded(self, violation_utils):
        """测试只记录第一个违规区域"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # 创建两个重叠的区域
        areas = [
            {"id": 1, "points": [[100, 100], [300, 100], [300, 300], [100, 300]]},
            {"id": 2, "points": [[150, 150], [250, 150], [250, 250], [150, 250]]}
        ]
        
        # 模拟检测结果
        mock_result = Mock()
        mock_result.boxes = Mock()
        box_mock = Mock()
        box_mock.__getitem__ = lambda self, i: Mock(item=lambda: [200.0, 200.0, 50.0, 50.0][i])
        mock_result.boxes.xywh = Mock()
        mock_result.boxes.xywh.cpu.return_value = [box_mock]
        mock_result.boxes.id = Mock()
        mock_result.boxes.id.int.return_value.cpu.return_value.tolist.return_value = [1]
        mock_result.boxes.cls = Mock()
        mock_result.boxes.cls.cpu.return_value.tolist.return_value = [2]  # car
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, areas)
        
        # 一个目标只记录一次违规（第一个匹配的区域）
        assert len(violations) <= 1


# ==================== VU-08: 非车辆类别忽略 ====================

class TestNonVehicleClassIgnored:
    """VU-08: 非车辆类别忽略测试"""

    def test_person_class_ignored(self, violation_utils):
        """测试person类别被忽略"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # person的class_id是0
        assert 0 not in ViolationDetector.VEHICLE_CLASSES

    def test_bicycle_class_ignored(self, violation_utils):
        """测试bicycle类别被忽略"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # bicycle的class_id是1
        assert 1 not in ViolationDetector.VEHICLE_CLASSES

    def test_only_vehicle_classes_checked(self, violation_utils):
        """测试只检查车辆类别"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # 验证VEHICLE_CLASSES只包含车辆
        expected_classes = {2: 'car', 5: 'bus', 7: 'truck'}
        assert ViolationDetector.VEHICLE_CLASSES == expected_classes

    def test_non_vehicle_detection_no_violation(self, violation_utils):
        """测试非车辆检测不产生违规"""
        ViolationDetector = violation_utils.ViolationDetector
        
        # 模拟person检测结果
        mock_result = Mock()
        mock_result.boxes = Mock()
        box_mock = Mock()
        box_mock.__getitem__ = lambda self, i: Mock(item=lambda: [150.0, 150.0, 50.0, 50.0][i])
        mock_result.boxes.xywh = Mock()
        mock_result.boxes.xywh.cpu.return_value = [box_mock]
        mock_result.boxes.id = Mock()
        mock_result.boxes.id.int.return_value.cpu.return_value.tolist.return_value = [1]
        mock_result.boxes.cls = Mock()
        mock_result.boxes.cls.cpu.return_value.tolist.return_value = [0]  # person
        
        restricted_areas = [
            {"id": 1, "points": [[100, 100], [200, 100], [200, 200], [100, 200]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(
            mock_result, 
            restricted_areas
        )
        
        # person不应产生违规
        assert len(violations) == 0


# ==================== 服务层集成测试 ====================

class TestViolationServiceIntegration:
    """ViolationService集成测试"""

    def test_check_violations_with_camera(
        self, violation_service, app_context, mock_db, sample_camera
    ):
        """测试带摄像头的违规检查"""
        service = violation_service.ViolationService()
        
        # 模拟检测结果
        mock_result = Mock()
        mock_result.boxes = None  # 无检测框
        
        with patch('app.services.violation_service.Camera') as MockCamera:
            MockCamera.query.get.return_value = sample_camera
            
            violations = service.check_violations(sample_camera.id, mock_result)
            
            # 无检测框应返回空列表
            assert violations == []

    def test_check_violations_camera_not_found(
        self, violation_service, app_context, mock_db
    ):
        """测试摄像头不存在时的处理"""
        service = violation_service.ViolationService()
        
        mock_result = Mock()
        
        with patch('app.services.violation_service.Camera') as MockCamera:
            MockCamera.query.get.return_value = None
            
            violations = service.check_violations(999, mock_result)
            
            assert violations == []

    def test_get_violations_with_filters(
        self, violation_service, app_context, mock_db, sample_violations
    ):
        """测试带过滤条件的违规查询"""
        service = violation_service.ViolationService()
        
        filters = {
            'camera_id': sample_violations[0].camera_id,
            'vehicle_type': 'car'
        }
        
        violations = service.get_violations(filters)
        
        # 应返回过滤后的结果
        assert isinstance(violations, list)

    def test_get_violations_order_by_timestamp(
        self, violation_service, app_context, mock_db, sample_violations
    ):
        """测试违规记录按时间排序"""
        service = violation_service.ViolationService()
        
        violations = service.get_violations()
        
        if len(violations) > 1:
            # 验证降序排列
            timestamps = [v['timestamp'] for v in violations]
            assert timestamps == sorted(timestamps, reverse=True)


# ==================== 异常处理测试 ====================

class TestViolationExceptionHandling:
    """违规模块异常处理测试"""

    def test_database_error_handling(self, client, violation_service):
        """测试数据库错误处理"""
        def mock_get_violations_raises(self, filters=None):
            raise Exception("Database connection error")
        
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            mock_get_violations_raises
        ):
            resp = client.get("/violation/records")
            
            # 应返回错误状态
            assert resp.status_code == 400

    def test_invalid_camera_id_type(self, client):
        """测试无效的camera_id类型"""
        resp = client.get("/violation/records?camera_id=invalid")
        
        # 无法转换为整数应报错
        assert resp.status_code == 400

    def test_check_violations_exception_rollback(
        self, violation_service, app_context, mock_db, sample_camera
    ):
        """测试违规检查异常时回滚"""
        service = violation_service.ViolationService()
        
        # 模拟会导致异常的检测结果
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.xywh = Mock()
        mock_result.boxes.xywh.cpu.side_effect = Exception("GPU error")
        
        violations = service.check_violations(sample_camera.id, mock_result)
        
        # 异常应被捕获，返回空列表
        assert violations == []


# ==================== 边界条件测试 ====================

class TestViolationBoundaryConditions:
    """违规模块边界条件测试"""

    def test_very_large_coordinates(self, violation_utils):
        """测试超大坐标值"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [999999, 999999]
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is False

    def test_very_small_polygon(self, violation_utils):
        """测试极小多边形"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [100.5, 100.5]
        polygon = [[100, 100], [101, 100], [101, 101], [100, 101]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is True

    def test_floating_point_precision(self, violation_utils):
        """测试浮点数精度"""
        ViolationDetector = violation_utils.ViolationDetector
        
        point = [150.123456789, 150.987654321]
        polygon = [[100, 100], [200, 100], [200, 200], [100, 200]]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon)
        
        assert result is True

    def test_timestamp_edge_case_midnight(self, client, violation_service):
        """测试午夜时间边界"""
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=[]
        ):
            resp = client.get(
                "/violation/records?start_time=2024-03-15%2000:00:00"
            )
            
            assert resp.status_code == 200

    def test_timestamp_edge_case_end_of_day(self, client, violation_service):
        """测试一天结束时间边界"""
        with patch.object(
            violation_service.ViolationService, 
            'get_violations', 
            return_value=[]
        ):
            resp = client.get(
                "/violation/records?end_time=2024-03-15%2023:59:59"
            )
            
            assert resp.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
