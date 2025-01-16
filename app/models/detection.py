from app import db


# 定义一个名为DetectionRecord的数据库模型类，继承自db.Model

class DetectionRecord(db.Model):
    # 定义主键，类型为整数，不允许为空
    id = db.Column(db.Integer, primary_key=True)

    # 定义车辆类型字段，类型为字符串，最大长度50，不允许为空
    vehicle_type = db.Column(db.String(50), nullable=False)

    # 定义检测时间字段，类型为日期时间，不允许为空
    detection_time = db.Column(db.DateTime, nullable=False)

    # 定义相机ID字段，类型为字符串，最大长度50，不允许为空
    camera_id = db.Column(db.String(50), nullable=False)
