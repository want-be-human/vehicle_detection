"""
配置文件 (config.py)

主要功能：
1. 数据库配置：
   - 配置MySQL连接URI
   - 设置数据库追踪选项
   - 配置SQL语句回显

2. 路径配置：
   - 模型文件路径
   - 配置文件路径
   - 静态资源路径

3. 应用配置：
   - 摄像头配置
   - WebSocket配置
   - 跨域设置
   - 缓存配置

与前端交互：
1. 视频流配置：
   - 帧率限制
   - 分辨率设置
   - 压缩质量

2. WebSocket设置：
   - 跨域允许
   - 心跳间隔
   - 重连策略

工作流程：
1. 应用启动时加载配置
2. 初始化各项服务
3. 建立数据库连接
4. 启动WebSocket服务
"""

import os

class Config:
     # 格式: mysql://用户名:密码@主机地址:端口/数据库名
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://root:Yun211314@localhost:3306/project')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = bool(os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true')
    MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
    CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'configs')
