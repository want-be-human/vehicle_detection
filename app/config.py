"""
config.py                 # 配置文件
"""

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
