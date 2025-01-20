from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.routes import auth, detection, admin

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    app.register_blueprint(auth.bp)
    app.register_blueprint(detection.bp)
    app.register_blueprint(admin.bp)

    return app
