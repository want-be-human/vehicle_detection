# tests/test_camera.py

import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from app.config.config import Config

if __name__ == '__main__':
    config = Config()
    print(f"Database URI: {config.SQLALCHEMY_DATABASE_URI}")
    print(f"SQLAlchemy Echo: {config.SQLALCHEMY_ECHO}")
    print(f"Model Directory: {config.MODEL_DIR}")
    print(f"Config Directory: {config.CONFIG_DIR}")