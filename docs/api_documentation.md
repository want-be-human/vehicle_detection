# 车辆检测系统 API 文档

## 目录
- [认证接口](#认证接口)
- [摄像头管理](#摄像头管理)
- [车辆检测](#车辆检测)
- [违规管理](#违规管理)
- [历史查询](#历史查询)
- [统计分析](#统计分析)
- [WebSocket 接口](#websocket-接口)

## 认证接口

### 用户注册
```http
POST /auth/register
```
请求体:
```json
{
    "username": "admin",
    "password": "123456",
    "role": "admin"
}
```
响应:
```json
{
    "message": "User registered successfully"
}
```

### 用户登录
```http
POST /auth/login
```
请求体:
```json
{
    "username": "admin",
    "password": "123456"
}
```
响应:
```json
{
    "token": "eyJ0eXA..."
}
```

## 摄像头管理

### 添加摄像头
```http
POST /camera/cameras
```
请求体:
```json
{
    "name": "摄像头1",
    "ip_address": "192.168.1.100",
    "port": 554,
    "url": "rtsp://192.168.1.100:554/stream1",
    "resolution": "1920x1080",
    "frame_rate": 30,
    "encoding_format": "H.264",
    "restricted_areas": [
        {
            "id": 1,
            "points": [[100,100], [200,100], [200,200], [100,200]]
        }
    ]
}
```

### 删除摄像头
```http
DELETE /camera/cameras/{camera_id}
```

## 车辆检测

### 启动检测
```http
POST /detection/detect
```
请求体:
```json
{
    "camera_id": 1,
    "stream_url": "rtsp://...",
    "model_path": "yolov8n.pt",
    "tracking_config": "botsort.yaml"
}
```

### 获取检测记录
```http
GET /detection/detections
```

### 获取处理状态
```http
GET /detection/status
```

### 配置视频流
```http
POST /detection/stream/config
```
请求体:
```json
{
    "max_width": 1280,
    "max_height": 720,
    "jpeg_quality": 80,
    "target_fps": 25
}
```

## 违规管理

### 获取违规记录
```http
GET /violation/records
```
查询参数:
- camera_id: 摄像头ID
- start_time: 开始时间 (YYYY-MM-DD HH:mm:ss)
- end_time: 结束时间
- vehicle_type: 车辆类型
- violation_type: 违规类型

## 历史查询

### 查询历史监控
```http
POST /history/query
```
请求体:
```json
{
    "year": 2024,
    "month": 3,
    "day": 15,
    "hour": 14,
    "camera_id": 1
}
```

## 统计分析

### 获取每日统计
```http
GET /statistics/daily?date=2024-03-15
```

### 获取统计图表
```http
GET /statistics/charts/2024-03-15
```

### 查询统计数据
```http
POST /statistics/query
```
请求体:
```json
{
    "type": "month",
    "range": "2024-03"
}
```

## WebSocket 接口

### 视频流
- 命名空间: `/video`
- 事件:
  - `video_frame`: 接收视频帧
  - `join_stream`: 加入视频流房间
  - `leave_stream`: 离开视频流房间

### 违规提醒
- 命名空间: `/violations`
- 事件:
  - `violation_alert`: 接收违规提醒
  - `join`: 加入摄像头房间

### 统计数据
- 命名空间: `/statistics`
- 事件:
  - `statistics_update`: 接收统计数据更新

## 数据格式

### 视频帧数据
```json
{
    "camera_id": 1,
    "frame": "base64编码的帧数据",
    "timestamp": 1647331200
}
```

### 违规提醒数据
```json
{
    "camera_id": 1,
    "camera_name": "摄像头1",
    "violation_type": "parking",
    "vehicle_type": "car",
    "location": {"x": 100, "y": 200},
    "timestamp": "2024-03-15 14:30:00"
}
```

### 统计数据
```json
{
    "date": "2024-03-15",
    "vehicle_distribution": {
        "car": 100,
        "bus": 50,
        "truck": 30
    },
    "hourly_flow": [
        {"hour": 0, "count": 30},
        {"hour": 1, "count": 25}
    ],
    "peak_hours": [
        {"hour": 8, "count": 100},
        {"hour": 17, "count": 120}
    ]
}
```

## 错误处理

所有接口在发生错误时返回:
```json
{
    "success": false,
    "message": "错误信息描述"
}
```

状态码说明:
- 200: 请求成功
- 400: 请求参数错误
- 401: 未授权
- 404: 资源不存在
- 500: 服务器内部错误
```