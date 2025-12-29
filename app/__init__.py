"""
Flask应用初始化模块 (__init__.py)

主要功能：
1. 应用初始化：
   - 创建Flask应用实例
   - 配置数据库连接
   - 初始化各种扩展
   - 注册所有蓝图路由

2. 核心组件初始化：
   - SQLAlchemy: 数据库ORM
   - Migrate: 数据库迁移
   - CORS: 跨域支持
   - SocketIO: WebSocket通信
   - Scheduler: 定时任务

3. 蓝图注册：
   - auth: 用户认证
   - camera: 摄像头管理
   - detection: 车辆检测
   - violation: 违规管理
   - history: 历史查询
   - statistics: 统计分析
   - plugins: 插件系统

与前端交互：
1. REST API:
   - /auth/*: 用户认证接口
   - /camera/*: 摄像头管理接口
   - /detection/*: 检测控制接口
   - /violation/*: 违规记录接口
   - /history/*: 历史查询接口
   - /statistics/*: 统计数据接口

2. WebSocket通信：
   - /video: 视频流传输
   - /violations: 违规提醒
   - /statistics: 实时统计
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.utils.websocket_utils import socketio
from app.config.config import Config

# 创建数据库实例
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # 如果需要跨域支持
    socketio.init_app(app, cors_allowed_origins="*")

     # 延迟导入避免循环引用
    from app.config.scheduler_config import scheduler

    # 初始化定时任务
    scheduler.start()
    # 可选：将统计任务的初始化抽离到其他函数中
    # schedule_tasks()

    # 注册蓝图
    from app.routes.connect import connect_blueprint
    from app.routes.auth import auth_blueprint
    from app.routes.camera import camera_blueprint
    from app.routes.detection import detection_blueprint
    from app.routes.violation import violation_blueprint
    from app.routes.history import history_blueprint
    from app.routes.statistics import statistics_blueprint
   #  from app.routes.plugins import plugins_blueprint

    app.register_blueprint(connect_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(camera_blueprint, url_prefix='/camera')
    app.register_blueprint(detection_blueprint, url_prefix='/detection')
    app.register_blueprint(violation_blueprint, url_prefix='/violation')
    app.register_blueprint(history_blueprint, url_prefix='/history')
    app.register_blueprint(statistics_blueprint, url_prefix='/statistics')
   #  app.register_blueprint(plugins_blueprint, url_prefix='/plugins')

    return app
