"""
违规检测和提醒服务 (ViolationService)

主要功能：
1. 违规检测：
   - 检测车辆是否在禁停区域
   - 根据车辆轨迹判断违规行为
   - 避免重复提醒(使用violation_cache)
   - 记录违规信息到数据库

2. 违规记录管理：
   - 存储违规记录
   - 支持多维度查询（摄像头、时间段、车型等）
   - 提供违规记录导出

与前端交互：
1. WebSocket实时推送:
   - 通过[`emit_violation_alert`](app/utils/websocket_utils.py)推送违规提醒
   - 包含摄像头名称、违规时间、车辆类型、坐标信息
   - 支持弹窗提醒和声音提示

2. REST API接口:
   - GET /violation/records: 获取违规记录
   - 支持多条件筛选查询

数据流向：
1. 实时检测:
   Detection -> ViolationDetector -> 违规判定
             -> 数据库存储 -> WebSocket -> 前端提醒

2. 历史查询:
   前端请求 -> REST API -> 数据库查询 -> 返回结果

工作流程：
1. 违规检测:
   - 获取摄像头禁停区域配置
   - 检查车辆位置是否在禁区内
   - 根据track_id避免重复提醒
   - 创建违规记录并存储

2. 提醒处理:
   - 检查违规间隔(>60s)
   - 生成违规记录
   - 推送实时提醒

异常处理：
- 数据库操作异常
- 检测结果解析异常
- 推送提醒异常

关联模块：
- [`Camera`](app/models/camera.py): 摄像头信息
- [`Violation`](app/models/violation.py): 违规记录
- [`ViolationDetector`](app/utils/violation_utils.py): 违规检测工具

数据缓存：
- violation_cache: 存储已提醒的违规记录
- 避免60秒内重复提醒同一违规

使用建议：
1. 建议在查询时添加适当的索引提升性能
2. 可以考虑添加违规等级分类
3. 可以扩展支持更多类型的违规行为
4. 考虑添加批量导出违规记录功能
"""                                      
from datetime import datetime
from app.utils.violation_utils import ViolationDetector
from app.models.camera import Camera
from app.models.detection import Detection
from app import db
from app.models.violation import Violation

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
                    
                    # 创建违规记录(使用新的Violation模型)
                    violation_record = Violation(
                        camera_id=camera_id,
                        camera_name=camera.name,
                        timestamp=current_time,
                        vehicle_type=violation['vehicle_type'],
                        location=str(violation['location']),
                        violation_type='parking',
                        area_id=violation['area_id']
                    )
                    db.session.add(violation_record)
                    
                    # 准备发送给前端的信息
                    new_violations.append(violation_record.to_dict())
            
            if new_violations:
                db.session.commit()
                
            return new_violations
            
        except Exception as e:
            db.session.rollback()
            print(f"Error checking violations: {str(e)}")
            return []

    def get_violations(self, filters=None):
        """获取违规记录"""
        try:
            query = Violation.query

            if filters:
                if 'camera_id' in filters:
                    query = query.filter_by(camera_id=filters['camera_id'])
                if 'start_time' in filters:
                    query = query.filter(Violation.timestamp >= filters['start_time'])
                if 'end_time' in filters:
                    query = query.filter(Violation.timestamp <= filters['end_time'])
                if 'vehicle_type' in filters:
                    query = query.filter_by(vehicle_type=filters['vehicle_type'])
                if 'violation_type' in filters:
                    query = query.filter_by(violation_type=filters['violation_type'])

            violations = query.order_by(Violation.timestamp.desc()).all()
            return [v.to_dict() for v in violations]
            
        except Exception as e:
            print(f"Error getting violations: {str(e)}")
            return []