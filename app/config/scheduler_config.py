"""
定时任务配置

本模块用于配置车辆检测应用中的定时任务，采用 APScheduler 库中的 BackgroundScheduler 来实现后台调度。
配置说明：
- executors:
    定义任务执行器，本例中采用 ThreadPoolExecutor，并设置最大线程数为 20，用于处理并发任务。
- job_defaults:
    指定任务的默认设置：
    - coalesce: 当任务在预定时间触发时是否合并（False 表示不合并）。
    - max_instances: 同一任务同时运行的最大实例数，限制为 3。
通过加载以上配置，BackgroundScheduler 可以在应用中高效管理和执行定时任务。


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
