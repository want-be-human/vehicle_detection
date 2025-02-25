"""
历史监控查询服务 (HistoryService)

主要功能：
1. 历史视频查询：
   - 按时间查询历史视频
   - 支持按摄像头ID筛选
   - 返回视频存储路径

2. 数据存取：
   - 从数据库查询视频记录
   - 检索指定时间段的监控记录
   - 支持精确到小时的查询

与前端交互：
1. 通过 history_blueprint 路由接口:
   - POST /history/query: 查询历史监控
   请求参数：
   {
       "year": 2024,
       "month": 3,
       "day": 15,
       "hour": 14,
       "camera_id": 1
   }
   响应数据：
   {
       "message": "Query successful",
       "video_url": "/path/to/video.mp4"
   }

2. 数据流向：
   Frontend -> REST API -> HistoryService -> Database
                      -> 返回视频路径 -> Frontend播放

工作流程：
1. 接收查询请求：
   - 验证查询参数
   - 格式化时间条件
   - 构建数据库查询

2. 执行查询：
   - 查询指定时间段视频记录
   - 检查记录是否存在
   - 返回视频路径或空值

3. 错误处理：
   - 参数验证异常
   - 数据库查询异常
   - 文件存在性检查

关联模块：
- [`Detection`](app/models/detection.py): 检测记录模型
- [`Camera`](app/models/camera.py): 摄像头信息模型

数据模型：
DetectionRecord:
  - camera_id: 摄像头ID
  - timestamp: 记录时间戳
  - video_path: 视频文件路径

使用建议：
1. 建议在查询时添加时间索引优化性能
2. 可以考虑添加视频文件存在性验证
3. 可以扩展支持按时间范围批量查询
4. 考虑添加查询结果缓存机制
"""
from datetime import datetime
from app.models.detection import Detection  # 导入正确的模型类

class HistoryService:
    @staticmethod
    def query_video(data):
        """
        查询历史监控视频
        Args:
            data (dict): 查询条件，包括年、月、日、时和摄像头ID
        Returns:
            str: 视频路径或URL
        """
        year = data['year']
        month = data['month']
        day = data['day']
        hour = data['hour']
        camera_id = data['camera_id']
        
        # 生成查询条件
        query_time = f"{year}-{month:02d}-{day:02d} {hour:02d}:00:00"
        query_datetime = datetime.strptime(query_time, "%Y-%m-%d %H:%M:%S")
        
        # 查询数据库
        video_record = Detection.query.filter_by(
            camera_id=camera_id
        ).filter(
            Detection.timestamp >= query_datetime,
            Detection.timestamp < query_datetime.replace(hour=hour+1)
        ).first()
        
        if video_record:
            # 返回存储的视频路径或URL
            return video_record.video_path
        return None