"""

违规检测和提醒服务
违规（禁停区域）：弹窗提醒摄像头名称、违规时间、违规车辆类型、坐标，并发声
提醒（特殊车辆出现时提醒）：将特殊车辆的摄像头名称、车辆类型、坐标呈现在前端

"""
from datetime import datetime
from app.utils.violation_utils import ViolationDetector
from app.models.camera import Camera
from app.models.detection import Detection
from app import db

class ViolationService:
    def __init__(self):
        self.violation_cache = {}  # 用于存储已提醒的违规记录
        
    def check_violations(self, camera_id, detection_result):
        """检查当前帧是否存在违规情况"""
        try:
            camera = Camera.query.get(camera_id)
            if not camera or not camera.restricted_areas:
                return []
                
            # 检查违规
            violations = ViolationDetector.check_vehicle_violation(
                detection_result, camera.restricted_areas)
            
            # 过滤并记录违规信息
            new_violations = []
            current_time = datetime.now()
            
            for violation in violations:
                # 生成违规记录键值
                violation_key = f"{camera_id}_{violation['track_id']}"
                
                # 检查是否需要提醒（避免重复提醒）
                if (violation_key not in self.violation_cache or 
                    (current_time - self.violation_cache[violation_key]).seconds > 60):
                    
                    self.violation_cache[violation_key] = current_time
                    
                    # 创建违规记录
                    violation_record = Detection(
                        camera_id=camera_id,
                        timestamp=current_time,
                        vehicle_type=violation['vehicle_type'],
                        location=str(violation['location']),
                        is_violation=True
                    )
                    db.session.add(violation_record)
                    
                    # 准备发送给前端的信息
                    new_violations.append({
                        "camera_name": camera.name,
                        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "vehicle_type": violation['vehicle_type'],
                        "location": violation['location'],
                        "area_id": violation['area_id']
                    })
            
            if new_violations:
                db.session.commit()
                
            return new_violations
            
        except Exception as e:
            db.session.rollback()
            print(f"Error checking violations: {str(e)}")
            return []