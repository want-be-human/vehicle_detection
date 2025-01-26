"""
违规检测和提醒工具：
违规（禁停区域）：用户可以手动划分每个摄像头的禁停区域

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
