"""
违规记录接口模块 (violation.py)

主要功能：
1. 违规记录查询：
   - 支持多条件筛选
   - 按摄像头ID过滤
   - 按时间范围查询
   - 按车辆类型筛选
   - 按违规类型筛选

REST API接口：
1. 获取违规记录：
   GET /records
   查询参数：
   - camera_id: 摄像头ID (整数)
   - start_time: 开始时间 (YYYY-MM-DD HH:mm:ss)
   - end_time: 结束时间 (YYYY-MM-DD HH:mm:ss)
   - vehicle_type: 车辆类型 (字符串)
   - violation_type: 违规类型 (字符串)

   响应：200 OK
   {
     "success": true,
     "violations": [
       {
         "id": 1,
         "camera_id": 1,
         "camera_name": "摄像头1",
         "timestamp": "2024-03-15 14:30:00",
         "vehicle_type": "car",
         "location": {"x": 100, "y": 200},
         "violation_type": "parking",
         "area_id": 1
       }
     ]
   }

   错误响应：400 Bad Request
   {
     "success": false,
     "message": "错误信息"
   }

工作流程：
1. 查询违规记录：
   Frontend GET /records 
   -> 解析查询参数
   -> ViolationService.get_violations()
   -> 查询数据库
   -> 返回结果

与其他模块关联：
- [`ViolationService`](app/services/violation_service.py): 违规记录服务
- [`Violation`](app/models/violation.py): 违规记录模型
- [`WebSocket`](app/utils/websocket_utils.py): 实时推送

数据流向：
1. 记录查询：
   Frontend请求 
   -> REST API 
   -> 数据库查询 
   -> Frontend展示

2. 实时违规：
   检测结果 -> 违规判定 
   -> 数据库存储 
   -> WebSocket推送

异常处理：
- 400: 请求参数错误
- 500: 服务器内部错误

使用建议：
1. 建议添加查询结果分页
2. 可以添加导出功能
3. 考虑添加缓存机制
4. 可以优化查询性能
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services.violation_service import ViolationService

violation_blueprint = Blueprint('violation', __name__)
violation_service = ViolationService()

@violation_blueprint.route('/records', methods=['GET'])
def get_violations():
    try:
        filters = {}
        
        camera_id = request.args.get('camera_id')
        if camera_id:
            filters['camera_id'] = int(camera_id)
            
        start_time = request.args.get('start_time')
        if start_time:
            filters['start_time'] = datetime.strptime(
                start_time, 
                '%Y-%m-%d %H:%M:%S'
            )
            
        end_time = request.args.get('end_time')
        if end_time:
            filters['end_time'] = datetime.strptime(
                end_time, 
                '%Y-%m-%d %H:%M:%S'
            )
            
        if 'vehicle_type' in request.args:
            filters['vehicle_type'] = request.args.get('vehicle_type')

        if 'violation_type' in request.args:
            filters['violation_type'] = request.args.get('violation_type')

        violations = violation_service.get_violations(filters)
        
        return jsonify({
            'success': True,
            'violations': violations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
