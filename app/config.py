"""
配置摄像头，模型路径等信息
"""

import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://root:Yun211314@host:port/database')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
    CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'configs')
