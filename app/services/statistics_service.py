"""
统计服务 (StatisticsService)

主要功能：
1. 统计数据生成与管理:
   - 计算每日车辆统计数据
   - 生成统计图表(饼图、折线图、柱状图)
   - 存储统计结果
   - 支持按年/月/周查询统计

2. 定时任务:
   - 每天0点自动生成前一天统计
   - 每小时更新当天实时统计

3. 数据可视化:
   - 车辆类型分布饼图
   - 分时段流量折线图
   - 高峰时段柱状图

与前端交互：
1. WebSocket实时推送:
   - 通过socketio推送统计数据更新
   - 命名空间: /statistics
   - 事件: statistics_update

2. REST API接口:
   - GET /statistics/daily: 获取每日统计
   - POST /statistics/query: 查询历史统计
   - GET /statistics/charts/<date>: 获取图表数据

数据流向：
1. 实时统计:
   Detection记录 -> 统计计算 -> WebSocket -> Frontend展示
                -> 数据库存储

2. 历史查询:
   Frontend请求 -> REST API -> 数据库查询 -> Frontend展示

工作流程：
1. 数据统计:
   - 聚合Detection记录
   - 计算各类统计指标
   - 生成图表数据
   - 存储统计结果

2. 定时更新:
   - 每天0点统计前一天数据
   - 每小时更新当天统计

3. 数据查询:
   - 支持多维度查询
   - 支持图表数据导出

图表类型：
1. vehicle_distribution:
   - 类型：饼图
   - 数据：各类车辆数量分布

2. hourly_flow:
   - 类型：折线图
   - 数据：24小时车流量变化

3. peak_hours:
   - 类型：柱状图
   - 数据：高峰时段流量

关联模型：
- [`Detection`](app/models/detection.py): 检测记录
- [`StatisticsModel`](app/models/statistics.py): 统计记录

性能优化：
- 使用缓存减少数据库查询
- 异步处理统计任务
- 优化图表数据结构
"""

from datetime import datetime, timedelta
from app.models.detection import Detection  
from app.models.statistics import StatisticsModel
from app.config.scheduler_config import scheduler
from app.utils.websocket_utils import socketio
from app import db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func
import json

class StatisticsService:
    @staticmethod
    def generate_charts(stats_data):
        """生成统计图表"""
        charts = {}
        
        # 生成车辆类型分布饼图
        if stats_data.get('vehicle_distribution'):
            fig = px.pie(
                values=list(stats_data['vehicle_distribution'].values()),
                names=list(stats_data['vehicle_distribution'].keys()),
                title='Vehicle Type Distribution'
            )
            charts['type_distribution'] = fig.to_json()
            
        # 生成分时段流量折线图
        if stats_data.get('hourly_flow'):
            hours = [item['hour'] for item in stats_data['hourly_flow']]
            counts = [item['count'] for item in stats_data['hourly_flow']]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hours, y=counts, mode='lines+markers'))
            fig.update_layout(title='Hourly Traffic Flow')
            charts['hourly_flow'] = fig.to_json()
            
        # 生成高峰时段柱状图
        if stats_data.get('peak_hours'):
            peak_data = pd.DataFrame(stats_data['peak_hours'])
            fig = px.bar(peak_data, x='hour', y='count', title='Peak Hours Traffic')
            charts['peak_hours'] = fig.to_json()
            
        return charts

    @staticmethod
    def calculate_daily_statistics(date=None):
        """计算每日统计数据"""
        if not date:
            date = datetime.now().date()
            
        start_time = datetime.combine(date, datetime.min.time())
        end_time = start_time + timedelta(days=1)
        
        # 使用正确的模型名称Detection
        detections = Detection.query.filter(
            Detection.timestamp.between(start_time, end_time)
        ).with_entities(
            Detection.timestamp,
            Detection.vehicle_type
        ).all()
        
        if not detections:
            return None
            
        df = pd.DataFrame(detections, columns=['timestamp', 'vehicle_type'])
        df['hour'] = df['timestamp'].dt.hour
        
        # 计算分时段流量
        hourly_flow = df.groupby('hour').size().reset_index(name='count')
        hourly_flow = hourly_flow.to_dict('records')
        
        # 计算车辆类型分布
        vehicle_distribution = df['vehicle_type'].value_counts().to_dict()
        
        # 计算高峰时段
        avg_flow = df.groupby('hour').size().mean()
        peak_hours = df.groupby('hour').size()
        peak_hours = [{'hour': h, 'count': c} for h, c in peak_hours[peak_hours > avg_flow].items()]
        
        stats_data = {
            'date': date,
            'peak_hours': peak_hours,
            'vehicle_distribution': vehicle_distribution,
            'hourly_flow': hourly_flow,
            'total_count': len(df)
        }
        
        # 生成图表数据
        stats_data['chart_data'] = StatisticsService.generate_charts(stats_data)
        
        # 保存/更新统计数据
        StatisticsService.save_statistics(stats_data)
        
        # 推送给前端
        socketio.emit('statistics_update', stats_data, namespace='/statistics')
        
        return stats_data

    @staticmethod
    def schedule_daily_statistics():
        """设置定时统计任务"""
        # 每天0点执行统计
        scheduler.add_job(
            StatisticsService.calculate_daily_statistics,
            'cron',
            hour=0,
            minute=0,
            id='daily_statistics',
            replace_existing=True
        )
        
        # 每小时更新当天统计
        scheduler.add_job(
            StatisticsService.calculate_daily_statistics,
            'cron',
            hour='*',
            id='hourly_statistics_update',
            replace_existing=True
        )

    @staticmethod
    def query_statistics_with_cache(query_params):
        """带缓存的统计查询"""
        cache_key = f"stats_{query_params['type']}_{query_params['range']}"
        
        # TODO: 实现缓存逻辑
        results = StatisticsModel.query.filter(
            # ...查询条件...
        ).options(
            db.joinedload('*')  # 优化关联查询
        ).all()
        
        return [r.to_dict() for r in results]

    @staticmethod
    def get_daily_statistics(date):
        """
        获取指定日期的车辆统计信息
        Args:
            date (str): 查询的日期（YYYY-MM-DD）
        Returns:
            dict: 统计信息，包括高峰期、分类计数等
        """
        start_time = datetime.strptime(date, "%Y-%m-%d")
        end_time = start_time + timedelta(days=1)

        # 使用正确的模型名称Detection
        records = Detection.query.filter(
            Detection.timestamp >= start_time,
            Detection.timestamp < end_time
        ).all()

        # 分类统计
        vehicle_count = {}
        hourly_count = [0] * 24  # 每小时车辆数量

        for record in records:
            hourly = record.timestamp.hour
            hourly_count[hourly] += 1

            vehicle_type = record.vehicle_type
            vehicle_count[vehicle_type] = vehicle_count.get(vehicle_type, 0) + 1

        avg_count = sum(hourly_count) / 24
        peak_hours = [i for i, count in enumerate(hourly_count) if count > avg_count]

        stats = {
            "date": date,
            "vehicle_count": vehicle_count,
            "hourly_count": hourly_count,
            "average": avg_count,
            "peak_hours": peak_hours
        }

        # 将统计结果存储到数据库
        StatisticsService.store_daily_statistics(date, stats)
        return stats

    @staticmethod
    def store_daily_statistics(date, stats):
        """
        存储每日统计信息
        Args:
            date (str): 日期
            stats (dict): 统计信息
        """
        stats_entry = StatisticsModel(
            date=date,
            statistics=json.dumps(stats)
        )
        db.session.add(stats_entry)
        db.session.commit()

    @staticmethod
    def query_statistics(data):
        """
        查询统计信息
        Args:
            data (dict): 查询类型和范围
        Returns:
            dict: 查询结果
        """
        query_type = data['type']  # 年、月、周
        range_value = data['range']

        # 构建查询范围
        if query_type == "year":
            start_time = datetime.strptime(f"{range_value}-01-01", "%Y-%m-%d")
            end_time = start_time.replace(year=start_time.year + 1)
        elif query_type == "month":
            start_time = datetime.strptime(f"{range_value}-01", "%Y-%m")
            end_time = start_time + timedelta(days=31)
        elif query_type == "week":
            start_time = datetime.strptime(range_value, "%Y-%m-%d")
            end_time = start_time + timedelta(days=7)
        else:
            return None

        records = StatisticsModel.query.filter(
            StatisticsModel.date >= start_time,
            StatisticsModel.date < end_time
        ).all()

        results = [json.loads(record.statistics) for record in records]
        return results
