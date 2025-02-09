"""
统计分析接口模块 (statistics.py)

主要功能：
1. 统计数据管理:
   - 获取每日车辆统计
   - 查询历史统计数据 
   - 生成统计图表
   - 获取统计概要

REST API接口：
1. 获取每日统计:
   GET /statistics/daily?date=2024-03-15
   响应：200 OK
   {
     "vehicle_count": {"car": 100, "bus": 50},
     "hourly_count": [0,0,0,...],
     "peak_hours": [8,17,18],
     "average": 85
   }

2. 查询统计数据:
   POST /statistics/query
   请求体：
   {
     "type": "month",  # year/month/week
     "range": "2024-03"
   }
   响应：200 OK
   [
     {
       "date": "2024-03-15",
       "stats": {...}
     }
   ]

3. 获取统计图表:
   GET /statistics/charts/2024-03-15
   响应：200 OK
   {
     "type_distribution": {...},  # 饼图数据
     "hourly_flow": {...},       # 折线图数据
     "peak_hours": {...}         # 柱状图数据
   }

4. 获取统计概要:
   GET /statistics/summary?start_date=2024-03-01&end_date=2024-03-15
   响应：200 OK
   {
     "total_vehicles": 1500,
     "peak_day": "2024-03-15",
     "vehicle_types": {...}
   }

工作流程：
1. 日常统计:
   Frontend GET /daily 
   -> StatisticsService.get_daily_statistics()
   -> 查询数据库
   -> 计算统计指标
   -> 返回结果

2. 历史查询:
   Frontend POST /query
   -> StatisticsService.query_statistics()
   -> 按条件检索
   -> 生成统计数据
   -> 返回结果

3. 图表生成:
   Frontend GET /charts/<date>
   -> StatisticsService.calculate_daily_statistics()
   -> 生成图表数据
   -> 返回JSON格式

与其他模块关联：
- [`StatisticsService`](app/services/statistics_service.py): 统计服务
- [`Detection`](app/models/detection.py): 检测记录模型
- [`StatisticsModel`](app/models/statistics.py): 统计数据模型

数据流向：
1. 实时统计:
   Detection记录 
   -> 统计计算 
   -> WebSocket推送
   -> Frontend展示

2. 历史查询:
   Frontend请求 
   -> 数据库查询 
   -> 统计处理 
   -> Frontend图表

异常处理：
- 400: 请求参数错误
- 404: 无统计数据
- 500: 服务器错误

使用建议：
1. 建议添加统计数据缓存机制
2. 可以扩展支持更多统计维度
3. 考虑添加数据导出功能
4. 可以优化大数据量查询性能
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services.statistics import StatisticsService

statistics_blueprint = Blueprint('statistics', __name__)

@statistics_blueprint.route('/daily', methods=['GET'])
def get_daily_statistics():
    """
    获取当天的车辆统计信息
    响应数据包括高峰期、每类车辆的数量统计等
    """
    date = request.args.get('date')  # 可选日期，默认为当天
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    stats = StatisticsService.get_daily_statistics(date)
    return jsonify(stats), 200


@statistics_blueprint.route('/query', methods=['POST'])
def query_statistics():
    """
    查询车辆统计信息（年、月、周）
    请求体包括：查询类型和范围
    """
    data = request.json
    result = StatisticsService.query_statistics(data)
    if result:
        return jsonify(result), 200
    return jsonify({"message": "No data available"}), 404

@statistics_blueprint.route('/charts/<date>', methods=['GET'])
def get_charts(date):
    """获取指定日期的统计图表"""
    try:
        stats = StatisticsService.calculate_daily_statistics(
            datetime.strptime(date, '%Y-%m-%d').date()
        )
        if stats and stats.get('chart_data'):
            return jsonify(stats['chart_data']), 200
        return jsonify({'message': 'No chart data available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@statistics_blueprint.route('/summary', methods=['GET'])
def get_summary():
    """获取统计概要信息"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        summary = StatisticsService.get_summary(start_date, end_date)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
