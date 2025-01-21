from app.models.detection import DetectionModel
from app.models.statistics import StatisticsModel
from datetime import datetime, timedelta
from app import db
import json

class StatisticsService:
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

        # 查询当天的车辆检测记录
        records = DetectionModel.query.filter(
            DetectionModel.timestamp >= start_time,
            DetectionModel.timestamp < end_time
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
