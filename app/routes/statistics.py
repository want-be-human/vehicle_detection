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
