"""
历史监控查询接口模块 (history.py)

主要功能：
1. 历史视频查询：
   - 按时间查询历史监控视频
   - 支持按摄像头ID筛选
   - 返回视频存储路径

REST API接口：
1. 查询历史监控：
   POST /history/query
   请求体格式：
   {
     "year": 2024,
     "month": 3,
     "day": 15,
     "hour": 14,
     "camera_id": 1
   }
   响应：200 OK
   {
     "message": "Query successful",
     "video_url": "/path/to/video.mp4"
   }
   
   错误响应：404 Not Found
   {
     "message": "No video found for the specified time and camera"
   }

工作流程：
1. 查询历史记录：
   Frontend POST /history/query 
   -> HistoryService.query_video()
   -> 查询数据库
   -> 验证文件存在性
   -> 返回视频路径

2. 视频回放：
   Frontend获取视频URL 
   -> 请求视频文件 
   -> 播放器显示

与其他模块关联：
- [`HistoryService`](app/services/history_service.py): 历史查询服务
- [`Detection`](app/models/detection.py): 检测记录模型
- [`Camera`](app/models/camera.py): 摄像头信息模型

数据存储结构：
- 视频按小时存储
- 文件命名格式：camera_{id}_{date}_{hour}.mp4
- 自动清理过期视频

异常处理：
- 404: 视频文件不存在
- 400: 请求参数错误
- 500: 服务器内部错误

使用建议：
1. 建议添加视频文件存在性验证
2. 可以扩展支持时间范围查询
3. 考虑添加视频文件预览功能
4. 可以添加查询结果缓存机制
"""
from flask import Blueprint, request, jsonify
from app.services.history_service import HistoryService

# 创建Blueprint实例
history_blueprint = Blueprint('history', __name__)

@history_blueprint.route('/query', methods=['POST'])
def query_history():
    """
    查询历史监控接口
    请求体包括：年、月、日、时、摄像头ID
    响应包括：对应视频的URL或路径
    """
    data = request.json
    video_url = HistoryService.query_video(data)
    if video_url:
        return jsonify({"message": "Query successful", "video_url": video_url}), 200
    return jsonify({"message": "No video found for the specified time and camera"}), 404

