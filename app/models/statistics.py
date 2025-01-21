from app import db

class StatisticsModel(db.Model):
    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)  # 日期
    statistics = db.Column(db.Text, nullable=False)  # 统计信息（JSON格式）

    def __repr__(self):
        return f"<Statistics(date={self.date})>"
