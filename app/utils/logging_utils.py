"""
提供摄像头检测的日志

"""

import logging

logger = logging.getLogger(__name__)

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)