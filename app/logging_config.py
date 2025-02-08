"""
配置日志格式和存储路径
"""

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

# 日志存储目录
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志格式
LOG_FORMAT = (
    "%(asctime)s [%(levelname)s] "
    "%(pathname)s:%(lineno)d - "
    "%(funcName)s: %(message)s"
)

def setup_logger():
    """配置日志系统"""
    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 清除现有的处理器
    logger.handlers.clear()

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    # 常规日志文件 - 按大小切割(10MB)
    normal_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "detection.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    normal_handler.setLevel(logging.INFO)
    normal_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(normal_handler)

    # 错误日志文件 - 按日期切割
    error_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "error.log"),
        when='midnight',
        interval=1,
        backupCount=30,  # 保留30天
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(error_handler)

    # 调试日志文件
    debug_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "debug.log"),
        maxBytes=20*1024*1024,  # 20MB
        backupCount=3,
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(debug_handler)

    return logger

# 初始化日志系统
logger = setup_logger()

# 定义一些常用的日志记录函数
def log_error(message, exc_info=True):
    """记录错误日志"""
    logger.error(message, exc_info=exc_info)

def log_info(message):
    """记录信息日志"""
    logger.info(message)

def log_debug(message):
    """记录调试日志"""
    logger.debug(message)

def log_warning(message):
    """记录警告日志"""
    logger.warning(message)