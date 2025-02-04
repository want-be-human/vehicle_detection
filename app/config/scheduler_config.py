"""
定时任务配置
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

scheduler_config = {
    'executors': {
        'default': ThreadPoolExecutor(20)
    },
    'job_defaults': {
        'coalesce': False,
        'max_instances': 3
    }
}

scheduler = BackgroundScheduler(scheduler_config)
