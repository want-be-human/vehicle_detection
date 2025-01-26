from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.utils.websocket_utils import socketio

# 创建数据库实例
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class="config.Config"):
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # 如果需要跨域支持
    socketio.init_app(app, cors_allowed_origins="*")

    # 注册蓝图
    from app.routes.auth import auth_blueprint
    from app.routes.camera import camera_blueprint
    from app.routes.detection import detection_blueprint
    from app.routes.alert import alert_blueprint
    from app.routes.violation import violation_blueprint
    from app.routes.history import history_blueprint
    from app.routes.statistics import statistics_blueprint
    from app.routes.plugins import plugins_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(camera_blueprint, url_prefix='/camera')
    app.register_blueprint(detection_blueprint, url_prefix='/detection')
    app.register_blueprint(alert_blueprint, url_prefix='/alert')
    app.register_blueprint(violation_blueprint, url_prefix='/violation')
    app.register_blueprint(history_blueprint, url_prefix='/history')
    app.register_blueprint(statistics_blueprint, url_prefix='/statistics')
    app.register_blueprint(plugins_blueprint, url_prefix='/plugins')

    return app
