"""
统计信息模型
记录年月日
统计信息（JSON格式）
    -高峰期（高于当天平均值）
    -当天车辆类型分布
    
"""

from app import db
from sqlalchemy import Index
from datetime import date as DateType
from typing import Optional, Any

class StatisticsModel(db.Model):
    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)  # 日期
    peak_hours = db.Column(db.JSON)  # 高峰时段 [{"hour": 8, "count": 100}, ...]
    vehicle_distribution = db.Column(db.JSON)  # 车辆类型分布 {"car": 100, "bus": 50, ...}
    hourly_flow = db.Column(db.JSON)  # 分时段流量 [{"hour": 0, "count": 30}, ...]
    total_count = db.Column(db.Integer, default=0)  # 总数，用于快速查询
    chart_data = db.Column(db.JSON)  # 图表数据 {"peak_chart": {...}, "distribution_chart": {...}}

    # 添加索引优化查询性能
    __table_args__ = (
        Index('idx_date_total', date, total_count),
        Index('idx_date', date),
    )

    def __init__(self, date: DateType, peak_hours: Optional[Any] = None,
                 vehicle_distribution: Optional[Any] = None, hourly_flow: Optional[Any] = None,
                 total_count: int = 0, chart_data: Optional[Any] = None):
        self.date = date
        self.peak_hours = peak_hours
        self.vehicle_distribution = vehicle_distribution
        self.hourly_flow = hourly_flow
        self.total_count = total_count
        self.chart_data = chart_data

    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'peak_hours': self.peak_hours,
            'vehicle_distribution': self.vehicle_distribution,
            'hourly_flow': self.hourly_flow,
            'total_count': self.total_count,
            'chart_data': self.chart_data
        }

    def __repr__(self):
        return f"<Statistics(date={self.date})>"
