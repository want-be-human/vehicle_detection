"""
app/                          # Flask应用代码
│   ├── __init__.py               # Flask应用初始化
│   ├── models/                   # 数据库模型
│   │   ├── user.py               # 用户模型
│   │   └── detection.py          # 车辆检测记录模型
│   ├── routes/                   # Flask路由（API接口）
│   │   ├── auth.py               # 用户认证相关接口
│   │   ├── detection.py          # 车辆检测相关接口
│   │   └── data.py               # 数据查询相关接口
│   ├── services/                 # 业务逻辑
│   │   ├── auth_service.py       # 用户认证服务
│   │   ├── detection_service.py  # 车辆检测服务
│   │   └── data_service.py       # 数据查询服务
│   ├── utils/                    # 工具函数
│   │   ├── image_processing.py   # 图像处理工具
│   │   └── yolo_integration.py   # YOLO算法集成
│   └── config.py                 # 配置文件
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # 加载配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/vehicle_detection'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    from app.routes import auth, detection, data
    app.register_blueprint(auth.bp)
    app.register_blueprint(detection.bp)
    app.register_blueprint(data.bp)

    return app