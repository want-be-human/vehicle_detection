# -*- coding: utf-8 -*-
"""
工具类测试 (test_utils.py)

覆盖所有工具类的测试:
- ViolationDetector: 违规检测工具
- WebSocket工具函数
- VideoStreamConfig: 视频流配置
- YOLOIntegration: YOLO集成
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestViolationDetector:
    """违规检测工具测试"""
    
    def test_is_point_in_polygon_inside(self, app_context):
        """测试点在多边形内"""
        from app.utils.violation_utils import ViolationDetector
        
        polygon_points = [[0, 0], [100, 0], [100, 100], [0, 100]]
        point = [50, 50]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon_points)
        
        assert result is True
    
    def test_is_point_in_polygon_outside(self, app_context):
        """测试点在多边形外"""
        from app.utils.violation_utils import ViolationDetector
        
        polygon_points = [[0, 0], [100, 0], [100, 100], [0, 100]]
        point = [150, 150]
        
        result = ViolationDetector.is_point_in_polygon(point, polygon_points)
        
        assert result is False
    
    def test_is_point_in_polygon_on_edge(self, app_context):
        """测试点在多边形边界上"""
        from app.utils.violation_utils import ViolationDetector
        
        polygon_points = [[0, 0], [100, 0], [100, 100], [0, 100]]
        point = [50, 0]  # 在边界上
        
        # 边界情况由shapely处理，可能返回True或False
        result = ViolationDetector.is_point_in_polygon(point, polygon_points)
        
        assert isinstance(result, bool)
    
    def test_is_point_in_polygon_complex(self, app_context):
        """测试复杂多边形"""
        from app.utils.violation_utils import ViolationDetector
        
        # L形多边形
        polygon_points = [
            [0, 0], [50, 0], [50, 50], [100, 50], 
            [100, 100], [0, 100]
        ]
        
        # 在L形内部
        result1 = ViolationDetector.is_point_in_polygon([25, 75], polygon_points)
        assert result1 is True
        
        # 在L形凹陷处
        result2 = ViolationDetector.is_point_in_polygon([75, 25], polygon_points)
        assert result2 is False
    
    def test_check_vehicle_violation_empty_areas(self, app_context):
        """测试违规检测 - 空禁区列表"""
        from app.utils.violation_utils import ViolationDetector
        
        mock_result = Mock()
        mock_result.boxes = Mock()
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, [])
        
        assert violations == []
    
    def test_check_vehicle_violation_no_boxes(self, app_context):
        """测试违规检测 - 无检测框"""
        from app.utils.violation_utils import ViolationDetector
        
        mock_result = Mock()
        mock_result.boxes = None
        
        restricted_areas = [
            {'id': 1, 'points': [[0, 0], [100, 0], [100, 100], [0, 100]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, restricted_areas)
        
        assert violations == []
    
    def test_check_vehicle_violation_vehicle_in_area(self, app_context):
        """测试违规检测 - 车辆在禁区内"""
        from app.utils.violation_utils import ViolationDetector
        import numpy as np_test
        
        # 创建mock检测结果
        mock_result = Mock()
        mock_result.boxes = Mock()
        
        # 使用numpy数组模拟真实的xywh数据
        xywh_data = np_test.array([[50.0, 50.0, 30.0, 20.0]])
        mock_boxes = Mock()
        mock_boxes.cpu.return_value = xywh_data
        mock_result.boxes.xywh = mock_boxes
        
        mock_ids = Mock()
        mock_ids.int.return_value.cpu.return_value.tolist.return_value = [1]
        mock_result.boxes.id = mock_ids
        
        mock_cls = Mock()
        mock_cls.cpu.return_value.tolist.return_value = [2]  # car
        mock_result.boxes.cls = mock_cls
        
        restricted_areas = [
            {'id': 1, 'points': [[0, 0], [100, 0], [100, 100], [0, 100]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, restricted_areas)
        
        assert len(violations) == 1
        assert violations[0]['vehicle_type'] == 'car'
        assert violations[0]['area_id'] == 1
    
    def test_check_vehicle_violation_vehicle_outside_area(self, app_context):
        """测试违规检测 - 车辆不在禁区"""
        from app.utils.violation_utils import ViolationDetector
        import numpy as np_test
        
        mock_result = Mock()
        mock_result.boxes = Mock()
        
        # 使用numpy数组模拟车辆位置在(200, 200) - 禁区外
        xywh_data = np_test.array([[200.0, 200.0, 30.0, 20.0]])
        mock_boxes = Mock()
        mock_boxes.cpu.return_value = xywh_data
        mock_result.boxes.xywh = mock_boxes
        
        mock_ids = Mock()
        mock_ids.int.return_value.cpu.return_value.tolist.return_value = [1]
        mock_result.boxes.id = mock_ids
        
        mock_cls = Mock()
        mock_cls.cpu.return_value.tolist.return_value = [2]  # car
        mock_result.boxes.cls = mock_cls
        
        restricted_areas = [
            {'id': 1, 'points': [[0, 0], [100, 0], [100, 100], [0, 100]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, restricted_areas)
        
        assert len(violations) == 0
    
    def test_check_vehicle_violation_non_vehicle_ignored(self, app_context):
        """测试违规检测 - 非车辆类别被忽略"""
        from app.utils.violation_utils import ViolationDetector
        
        mock_result = Mock()
        mock_result.boxes = Mock()
        
        mock_boxes = Mock()
        mock_boxes.cpu.return_value = [[50, 50, 30, 20]]
        mock_result.boxes.xywh = mock_boxes
        
        mock_ids = Mock()
        mock_ids.int.return_value.cpu.return_value.tolist.return_value = [1]
        mock_result.boxes.id = mock_ids
        
        mock_cls = Mock()
        mock_cls.cpu.return_value.tolist.return_value = [0]  # person - 非车辆
        mock_result.boxes.cls = mock_cls
        
        restricted_areas = [
            {'id': 1, 'points': [[0, 0], [100, 0], [100, 100], [0, 100]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, restricted_areas)
        
        assert len(violations) == 0
    
    def test_check_vehicle_violation_multiple_areas(self, app_context):
        """测试违规检测 - 多个禁区"""
        from app.utils.violation_utils import ViolationDetector
        import numpy as np_test
        
        mock_result = Mock()
        mock_result.boxes = Mock()
        
        xywh_data = np_test.array([[50.0, 50.0, 30.0, 20.0]])
        mock_boxes = Mock()
        mock_boxes.cpu.return_value = xywh_data
        mock_result.boxes.xywh = mock_boxes
        
        mock_ids = Mock()
        mock_ids.int.return_value.cpu.return_value.tolist.return_value = [1]
        mock_result.boxes.id = mock_ids
        
        mock_cls = Mock()
        mock_cls.cpu.return_value.tolist.return_value = [2]  # car
        mock_result.boxes.cls = mock_cls
        
        restricted_areas = [
            {'id': 1, 'points': [[0, 0], [100, 0], [100, 100], [0, 100]]},
            {'id': 2, 'points': [[200, 200], [300, 200], [300, 300], [200, 300]]}
        ]
        
        violations = ViolationDetector.check_vehicle_violation(mock_result, restricted_areas)
        
        # 车辆只在第一个禁区
        assert len(violations) == 1
        assert violations[0]['area_id'] == 1
    
    def test_vehicle_classes(self, app_context):
        """测试车辆类别配置"""
        from app.utils.violation_utils import ViolationDetector
        
        assert 2 in ViolationDetector.VEHICLE_CLASSES  # car
        assert 5 in ViolationDetector.VEHICLE_CLASSES  # bus
        assert 7 in ViolationDetector.VEHICLE_CLASSES  # truck


class TestVideoStreamConfig:
    """视频流配置测试"""
    
    def test_default_values(self, app_context):
        """测试默认配置值"""
        from app.utils.websocket_utils import VideoStreamConfig
        
        # 验证配置类有这些属性且值在合理范围内
        assert hasattr(VideoStreamConfig, 'MAX_WIDTH')
        assert hasattr(VideoStreamConfig, 'MAX_HEIGHT')
        assert hasattr(VideoStreamConfig, 'JPEG_QUALITY')
        assert hasattr(VideoStreamConfig, 'TARGET_FPS')
        
        # 验证值在合理范围内
        assert 640 <= VideoStreamConfig.MAX_WIDTH <= 4096
        assert 480 <= VideoStreamConfig.MAX_HEIGHT <= 2160
        assert 1 <= VideoStreamConfig.JPEG_QUALITY <= 100
        assert 1 <= VideoStreamConfig.TARGET_FPS <= 120
    
    def test_config_modification(self, app_context):
        """测试配置修改"""
        from app.utils.websocket_utils import VideoStreamConfig
        
        original_width = VideoStreamConfig.MAX_WIDTH
        VideoStreamConfig.MAX_WIDTH = 1920
        
        assert VideoStreamConfig.MAX_WIDTH == 1920
        
        # 恢复
        VideoStreamConfig.MAX_WIDTH = original_width


class TestWebSocketUtils:
    """WebSocket工具函数测试"""
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_violation_alert_with_camera(self, mock_socketio, app_context):
        """测试发送违规提醒 - 指定摄像头"""
        from app.utils.websocket_utils import emit_violation_alert
        
        violation_data = {
            'camera_id': 1,
            'violation_type': 'parking',
            'location': {'x': 100, 'y': 100},
            'timestamp': '2024-03-15 10:00:00',
            'vehicle_type': 'car'
        }
        
        emit_violation_alert(violation_data)
        
        mock_socketio.emit.assert_called_once()
        call_args = mock_socketio.emit.call_args
        assert call_args[0][0] == 'violation_alert'
        assert call_args[1]['namespace'] == '/violations'
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_violation_alert_without_camera(self, mock_socketio, app_context):
        """测试发送违规提醒 - 广播"""
        from app.utils.websocket_utils import emit_violation_alert
        
        violation_data = {
            'violation_type': 'parking',
            'timestamp': '2024-03-15 10:00:00'
        }
        
        emit_violation_alert(violation_data)
        
        mock_socketio.emit.assert_called_once()
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_violation_alert_exception(self, mock_socketio, app_context):
        """测试发送违规提醒 - 异常处理"""
        from app.utils.websocket_utils import emit_violation_alert
        
        mock_socketio.emit.side_effect = Exception('Socket error')
        
        # 不应抛出异常
        emit_violation_alert({'camera_id': 1})
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_special_vehicle_alert(self, mock_socketio, app_context):
        """测试发送特殊车辆提醒"""
        from app.utils.websocket_utils import emit_special_vehicle_alert
        
        alert_data = {
            'camera_name': 'Test Camera',
            'vehicles': [{'type': 'bus', 'track_id': 1}],
            'timestamp': '2024-03-15 10:00:00'
        }
        
        emit_special_vehicle_alert(alert_data)
        
        mock_socketio.emit.assert_called_once()
        call_args = mock_socketio.emit.call_args
        assert call_args[0][0] == 'special_vehicle_alert'
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_camera_status(self, mock_socketio, app_context):
        """测试发送摄像头状态"""
        from app.utils.websocket_utils import emit_camera_status
        
        emit_camera_status(1, 'online')
        
        mock_socketio.emit.assert_called_once()
        call_args = mock_socketio.emit.call_args
        assert call_args[0][0] == 'camera_status'
        assert call_args[0][1]['camera_id'] == 1
        assert call_args[0][1]['status'] == 'online'
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_detection_stats(self, mock_socketio, app_context):
        """测试发送检测统计"""
        from app.utils.websocket_utils import emit_detection_stats
        
        stats_data = {
            'vehicle_count': {'car': 100},
            'timestamp': '2024-03-15 10:00:00'
        }
        
        emit_detection_stats(stats_data)
        
        mock_socketio.emit.assert_called_once()
        call_args = mock_socketio.emit.call_args
        assert call_args[0][0] == 'detection_stats'
    
    @patch('app.utils.websocket_utils.socketio')
    @patch('app.utils.websocket_utils.cv2')
    def test_emit_video_frame(self, mock_cv2, mock_socketio, app_context):
        """测试发送视频帧"""
        from app.utils.websocket_utils import emit_video_frame
        
        # 模拟帧数据
        frame = Mock()
        frame.shape = (720, 1280, 3)
        
        mock_cv2.resize.return_value = frame
        mock_cv2.imencode.return_value = (True, Mock(tobytes=Mock(return_value=b'fake')))
        mock_cv2.IMWRITE_JPEG_QUALITY = 1
        
        emit_video_frame(1, frame)
        
        mock_socketio.emit.assert_called_once()
    
    @patch('app.utils.websocket_utils.socketio')
    @patch('app.utils.websocket_utils.cv2')
    def test_emit_video_frame_with_resize(self, mock_cv2, mock_socketio, app_context):
        """测试发送视频帧 - 需要缩放"""
        from app.utils.websocket_utils import emit_video_frame
        
        # 模拟大尺寸帧
        frame = Mock()
        frame.shape = (1080, 1920, 3)  # 大于配置的最大值
        
        resized_frame = Mock()
        resized_frame.shape = (720, 1280, 3)
        mock_cv2.resize.return_value = resized_frame
        mock_cv2.imencode.return_value = (True, Mock(tobytes=Mock(return_value=b'fake')))
        mock_cv2.IMWRITE_JPEG_QUALITY = 1
        mock_cv2.INTER_AREA = 3
        
        emit_video_frame(1, frame)
        
        # 验证resize被调用
        mock_cv2.resize.assert_called_once()
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_error(self, mock_socketio, app_context):
        """测试发送错误事件"""
        from app.utils.websocket_utils import emit_error
        
        emit_error('/test', {'message': 'Error occurred'})
        
        mock_socketio.emit.assert_called_once()
        call_args = mock_socketio.emit.call_args
        assert call_args[0][0] == 'error'
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_streaming_status(self, mock_socketio, app_context):
        """测试发送流媒体状态"""
        from app.utils.websocket_utils import emit_streaming_status
        
        emit_streaming_status(1, 'started')
        
        mock_socketio.emit.assert_called_once()
        call_args = mock_socketio.emit.call_args
        assert call_args[0][0] == 'streaming_start'
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_streaming_result(self, mock_socketio, app_context):
        """测试发送流媒体结果状态"""
        from app.utils.websocket_utils import emit_streaming_result
        
        emit_streaming_result(1, 'started')
        
        mock_socketio.emit.assert_called_once()


class TestYOLOIntegration:
    """YOLO集成测试"""
    
    @patch('app.utils.yolo_integration.os.path.exists')
    def test_init_invalid_model(self, mock_exists, app_context):
        """测试初始化 - 模型不存在"""
        from app.utils.yolo_integration import YOLOIntegration
        
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            YOLOIntegration('nonexistent.pt')
    
    @patch('app.utils.yolo_integration.os.path.exists')
    def test_init_invalid_tracker(self, mock_exists, app_context):
        """测试初始化 - 无效跟踪器"""
        from app.utils.yolo_integration import YOLOIntegration
        
        mock_exists.return_value = True
        
        with pytest.raises(ValueError):
            YOLOIntegration('model.pt', tracker_type='invalid_tracker')
    
    @patch('app.utils.yolo_integration.os.path.exists')
    def test_init_custom_tracker_no_config(self, mock_exists, app_context):
        """测试初始化 - 自定义跟踪器无配置"""
        from app.utils.yolo_integration import YOLOIntegration
        
        mock_exists.side_effect = [True, False]  # 模型存在，配置不存在
        
        with pytest.raises(ValueError):
            YOLOIntegration('model.pt', tracker_type='custom')
    
    @patch('app.utils.yolo_integration.os.path.exists')
    def test_init_success(self, mock_exists, app_context):
        """测试初始化成功"""
        from app.utils.yolo_integration import YOLOIntegration
        
        mock_exists.return_value = True
        
        yolo = YOLOIntegration('yolov8n.pt', tracker_type='botsort')
        
        assert yolo.tracker_type == 'botsort'
        assert yolo.tracking_config == 'botsort.yaml'
    
    @patch('app.utils.yolo_integration.os.path.exists')
    def test_init_with_custom_special_vehicles(self, mock_exists, app_context):
        """测试初始化 - 自定义特殊车辆"""
        from app.utils.yolo_integration import YOLOIntegration
        
        mock_exists.return_value = True
        
        custom_vehicles = {
            5: {'name': 'custom_bus', 'color': (255, 255, 0)}
        }
        
        yolo = YOLOIntegration('model.pt', special_vehicles=custom_vehicles)
        
        assert yolo.special_vehicles == custom_vehicles
    
    def test_target_classes(self, app_context):
        """测试目标类别配置"""
        from app.utils.yolo_integration import YOLOIntegration
        
        expected_classes = {0: 'person', 1: 'bicycle', 2: 'car', 
                          3: 'motorcycle', 5: 'bus', 7: 'truck'}
        
        assert YOLOIntegration.TARGET_CLASSES == expected_classes
    
    def test_special_vehicles_default(self, app_context):
        """测试默认特殊车辆配置"""
        from app.utils.yolo_integration import YOLOIntegration
        
        assert 5 in YOLOIntegration.SPECIAL_VEHICLES  # bus
        assert 7 in YOLOIntegration.SPECIAL_VEHICLES  # truck
    
    def test_tracker_options(self, app_context):
        """测试跟踪器选项"""
        from app.utils.yolo_integration import YOLOIntegration
        
        assert 'botsort' in YOLOIntegration.TRACKER_OPTIONS
        assert 'bytetrack' in YOLOIntegration.TRACKER_OPTIONS
        assert 'custom' in YOLOIntegration.TRACKER_OPTIONS


class TestLoggingConfig:
    """日志配置测试"""
    
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_setup_logger(self, mock_exists, mock_makedirs, app_context):
        """测试日志配置"""
        mock_exists.return_value = True
        
        # 测试logger创建
        # 注意：实际测试可能需要更多mock
    
    def test_log_format(self, app_context):
        """测试日志格式"""
        from app.logging_config import LOG_FORMAT
        
        assert '%(asctime)s' in LOG_FORMAT
        assert '%(levelname)s' in LOG_FORMAT
        assert '%(pathname)s' in LOG_FORMAT
    
    def test_log_directory(self, app_context):
        """测试日志目录"""
        from app.logging_config import LOG_DIR
        
        assert LOG_DIR == 'logs'


class TestLoggingUtils:
    """日志工具测试"""
    
    def test_log_info(self, app_context):
        """测试info日志"""
        from app.utils.logging_utils import log_info
        
        # 应该不抛异常
        log_info("Test info message")
    
    def test_log_error(self, app_context):
        """测试error日志"""
        from app.utils.logging_utils import log_error
        
        # 应该不抛异常
        log_error("Test error message")
    
    def test_log_detection(self, app_context):
        """测试detection日志"""
        from app.utils.logging_utils import log_detection
        
        # 应该不抛异常
        log_detection("Test detection message")


class TestYOLOIntegrationAdvanced:
    """YOLO集成高级测试"""
    
    @patch('app.utils.yolo_integration.os.path.exists')
    def test_init_custom_tracker_with_valid_config(self, mock_exists, app_context):
        """测试初始化自定义跟踪器 - 有效配置"""
        from app.utils.yolo_integration import YOLOIntegration
        
        # 模型存在，配置也存在
        mock_exists.return_value = True
        
        yolo = YOLOIntegration('model.pt', tracker_type='custom', tracking_config='custom_config.yaml')
        
        assert yolo.tracker_type == 'custom'
        assert yolo.tracking_config == 'custom_config.yaml'
    
    @patch('app.utils.yolo_integration.os.path.exists')
    def test_init_bytetrack_tracker(self, mock_exists, app_context):
        """测试初始化bytetrack跟踪器"""
        from app.utils.yolo_integration import YOLOIntegration
        
        mock_exists.return_value = True
        
        yolo = YOLOIntegration('model.pt', tracker_type='bytetrack')
        
        assert yolo.tracker_type == 'bytetrack'
        assert yolo.tracking_config == 'bytetrack.yaml'
    
    @patch('app.utils.yolo_integration.os.path.exists')
    @patch('app.utils.yolo_integration.YOLO')
    @patch('app.utils.yolo_integration.ViolationService')
    def test_run_tracker_in_thread_exception(self, mock_vs, mock_yolo, mock_exists, app_context):
        """测试跟踪器线程异常处理"""
        from app.utils.yolo_integration import YOLOIntegration
        
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_model.track.side_effect = Exception("Connection error")
        mock_yolo.return_value = mock_model
        
        yolo = YOLOIntegration('model.pt')
        
        with pytest.raises(Exception):
            list(yolo.run_tracker_in_thread(1, 'rtsp://test'))
    
    @patch('app.utils.yolo_integration.os.path.exists')
    @patch('app.utils.yolo_integration.threading.Thread')
    def test_start_stream_processing(self, mock_thread, mock_exists, app_context):
        """测试启动流处理"""
        from app.utils.yolo_integration import YOLOIntegration
        
        mock_exists.return_value = True
        mock_thread_instance = MagicMock()
        mock_thread_instance.ident = 12345
        mock_thread.return_value = mock_thread_instance
        
        yolo = YOLOIntegration('model.pt')
        
        result = yolo.start_stream_processing(1, 'rtsp://test', 'output.mp4')
        
        assert result['thread_id'] == 12345
        assert result['status'] == 'running'
        assert result['camera_id'] == 1
        mock_thread_instance.start.assert_called_once()


class TestWebSocketUtilsAdvanced:
    """WebSocket工具高级测试"""
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_violation_alert_exception(self, mock_socketio, app_context):
        """测试发送违规提醒 - 异常处理"""
        from app.utils.websocket_utils import emit_violation_alert
        
        mock_socketio.emit.side_effect = Exception("Socket error")
        
        # 应该不抛异常（被捕获）
        violation_data = {'camera_id': 1, 'violation_type': 'parking'}
        emit_violation_alert(violation_data)
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_camera_status_exception(self, mock_socketio, app_context):
        """测试发送摄像头状态 - 异常处理"""
        from app.utils.websocket_utils import emit_camera_status
        
        mock_socketio.emit.side_effect = Exception("Socket error")
        
        # 应该不抛异常（被捕获）
        emit_camera_status(1, 'online')
    
    @patch('app.utils.websocket_utils.socketio')
    def test_emit_detection_stats_exception(self, mock_socketio, app_context):
        """测试发送检测统计 - 异常处理"""
        from app.utils.websocket_utils import emit_detection_stats
        
        mock_socketio.emit.side_effect = Exception("Socket error")
        
        # 应该不抛异常（被捕获）
        stats_data = {'total_vehicles': 100, 'total_violations': 5}
        emit_detection_stats(stats_data)
    
    @patch('app.utils.websocket_utils.socketio')
    @patch('cv2.resize')
    @patch('cv2.imencode')
    def test_emit_video_frame_exception(self, mock_imencode, mock_resize, mock_socketio, app_context):
        """测试发送视频帧 - 异常处理"""
        from app.utils.websocket_utils import emit_video_frame
        import numpy as np_local
        
        mock_socketio.emit.side_effect = Exception("Socket error")
        mock_imencode.return_value = (True, np_local.array([1, 2, 3], dtype=np_local.uint8))
        
        frame = np_local.zeros((480, 640, 3), dtype=np_local.uint8)
        
        # 应该不抛异常（被捕获）
        emit_video_frame(1, frame)