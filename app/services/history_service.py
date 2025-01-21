"""
数据查询服务
"""
from datetime import datetime
from app.models.detection import DetectionRecord  # 导入正确的模型类

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
        video_record = DetectionRecord.query.filter_by(
            camera_id=camera_id
        ).filter(
            DetectionRecord.timestamp >= query_datetime,
            DetectionRecord.timestamp < query_datetime.replace(hour=hour+1)
        ).first()
        
        if video_record:
            # 返回存储的视频路径或URL
            return video_record.video_path
        return None