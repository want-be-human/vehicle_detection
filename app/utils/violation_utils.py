"""
违规检测工具类 (ViolationDetector)

主要功能：
1. 违规检测：
   - 检测车辆是否在禁停区域内
   - 支持多边形区域检测
   - 支持多种车辆类型识别 (car/bus/truck)
   - 基于目标检测结果进行违规判定

2. 空间关系判断：
   - 判断点是否在多边形内
   - 使用 shapely 库进行几何计算
   - 支持复杂多边形区域

检测流程：
1. 输入处理：
   - 接收 YOLO 检测结果
   - 获取目标框坐标
   - 获取跟踪 ID
   - 获取类别信息

2. 违规判定：
   - 提取车辆中心点坐标
   - 检查是否在禁停区域内
   - 生成违规信息记录

3. 结果输出：
   - 返回违规信息列表
   - 包含车辆类型、位置、区域信息

与其他模块交互：
1. 输入接口：
   - 从 [`DetectionService`](app/services/detection_service.py) 接收检测结果
   - 从 [`Camera`](app/models/camera.py) 获取禁停区域配置

2. 输出接口：
   - 向 [`ViolationService`](app/services/violation_service.py) 提供违规检测结果
   - 通过 WebSocket 推送给前端

数据格式：
1. 禁停区域格式：
   [
     {
       "id": 1,
       "points": [[x1,y1], [x2,y2], ...]
     },
     ...
   ]

2. 违规信息格式：
   {
     "track_id": 跟踪ID,
     "vehicle_type": 车辆类型,
     "location": {"x": x坐标, "y": y坐标},
     "area_id": 区域ID
   }

注意事项：
1. 确保禁停区域坐标正确性
2. 考虑点在边界上的情况
3. 注意坐标系的一致性

优化建议：
1. 可添加车辆停留时间判断
2. 可扩展支持更多违规类型
3. 可优化空间查询性能
"""
import numpy as np
from shapely.geometry import Point, Polygon

class ViolationDetector:
    # 需要检查的车辆类别
    VEHICLE_CLASSES = {2: 'car', 5: 'bus', 7: 'truck'}
    
    @staticmethod
    def is_point_in_polygon(point, polygon_points):
        """判断点是否在多边形内"""
        point = Point(point)
        polygon = Polygon(polygon_points)
        return polygon.contains(point)

    @staticmethod
    def check_vehicle_violation(detection_result, restricted_areas):
        """
        检查车辆是否在禁停区域内
        Args:
            detection_result: YOLO检测结果
            restricted_areas: 禁停区域列表
        Returns:
            violations: 违规信息列表
        """
        if not restricted_areas or detection_result.boxes is None:
            return []
            
        violations = []
        boxes = detection_result.boxes.xywh.cpu()  # 获取中心点坐标和宽高
        track_ids = detection_result.boxes.id.int().cpu().tolist()
        cls_ids = detection_result.boxes.cls.cpu().tolist()
        
        # 遍历所有检测到的目标
        for box, track_id, cls_id in zip(boxes, track_ids, cls_ids):
            # 仅检查车辆类别
            if int(cls_id) in ViolationDetector.VEHICLE_CLASSES:
                x, y = box[0].item(), box[1].item()  # 获取中心点坐标
                
                # 检查每个禁停区域
                for area in restricted_areas:
                    if ViolationDetector.is_point_in_polygon([x, y], area['points']):
                        violations.append({
                            'track_id': track_id,
                            'vehicle_type': ViolationDetector.VEHICLE_CLASSES[int(cls_id)],
                            'location': {'x': int(x), 'y': int(y)},
                            'area_id': area['id']
                        })
                        break  # 一个目标只记录一次违规
                        
        return violations
