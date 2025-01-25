"""
统计信息模型
记录年月日
统计信息（JSON格式）
    -高峰期（高于当天平均值）
    -当天车辆类型分布
    
"""

from app import db

class StatisticsModel(db.Model):
    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)  # 日期
    statistics = db.Column(db.Text, nullable=False)  # 统计信息（JSON格式）

    def __repr__(self):
        return f"<Statistics(date={self.date})>"
