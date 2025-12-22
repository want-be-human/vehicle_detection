# 车辆检测与管理系统

## 项目简介

本项目是一个基于Python Flask的车辆检测与管理系统，使用YOLO模型进行实时车辆检测，支持违规行为识别、特殊车辆监控等功能。

## 主要功能

1. **车辆检测**
   - 实时视频流处理
   - 多摄像头支持
   - 特殊车辆识别
   - 违规行为检测

2. **数据管理**
   - 历史记录查询
   - 统计数据分析
   - 违规记录管理
   - 实时数据展示

3. **系统功能**
   - 用户权限管理
   - 摄像头配置
   - 插件系统扩展
   - 日志记录

## 技术栈

- **后端框架**: Flask
- **数据库**: MySQL
- **目标检测**: YOLOv11
- **实时通信**: Flask-SocketIO
- **权限认证**: JWT
- **数据分析**: Pandas, Plotly

## 快速开始

### 1. 环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

```python
# 在config.py中配置数据库连接
SQLALCHEMY_DATABASE_URI = 'mysql://用户名:密码@主机:端口/数据库名'
```

### 3. 初始化数据库

```bash
python scripts/setup_db.py
```

### 4. 启动服务器

```bash
python run.py
```

## API接口

详细的API文档请参考 api_documentation.md

### 主要接口示例：

1. **用户认证**
   ```http
   POST /auth/login
   POST /auth/register
   ```

2. **摄像头管理**
   ```http
   POST /cameras
   DELETE /cameras/{id}
   ```

3. **检测控制**
   ```http
   POST /detect
   GET /detections
   ```

## 项目结构

```markdown
vehicle-detection-system/
├── app/                    # 应用核心代码
│   ├── __init__.py          # 应用初始化
│   ├── config/              # 配置文件
│   │   ├── __init__.py
│   │   └── scheduler_config.py    # 定时任务配置
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── camera.py         # 摄像头模型
│   │   ├── detection.py      # 检测记录模型
│   │   ├── statistics.py     # 统计数据模型
│   │   ├── user.py          # 用户模型
│   │   └── violation.py      # 违规记录模型
│   ├── routes/             # API路由
│   │   ├── __init__.py
│   │   ├── admin.py         # 管理员接口
│   │   ├── auth.py          # 认证接口
│   │   ├── camera.py        # 摄像头管理
│   │   ├── detection.py     # 检测管理
│   │   ├── history.py       # 历史查询
│   │   ├── statistics.py    # 统计分析
│   │   └── violation.py     # 违规管理
│   ├── services/          # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth_service.py     # 认证服务
│   │   ├── camera_service.py   # 摄像头服务
│   │   ├── detection_service.py # 检测服务
│   │   ├── history_service.py  # 历史查询服务
│   │   ├── statistics_service.py # 统计服务
│   │   └── violation_service.py # 违规服务
│   ├── utils/             # 工具函数
│   │   ├── __init__.py
│   │   ├── camera_utils.py     # 摄像头工具
│   │   ├── image_processing.py # 图像处理
│   │   ├── logging_utils.py    # 日志工具
│   │   ├── violation_utils.py  # 违规检测工具
│   │   ├── websocket_utils.py  # WebSocket工具
│   │   └── yolo_integration.py # YOLO集成
│   ├── plugins/           # 插件系统
│   │   ├── __init__.py
│   │   ├── example_plugin.py   # 示例插件
│   │   └── plugin_template.py  # 插件模板
│   ├── events/            # 事件处理
│   │   └── websocket_events.py # WebSocket事件
│   └── assets/           # 资源文件
│       ├── models/       # 模型文件
│       │   └── yolov8n.pt
│       └── configs/      # 配置文件
│           └── custom_config.yaml
├── docs/                 # 项目文档
│   ├── api_documentation.md    # API文档
│   ├── plugin_development_guide.md # 插件开发指南
│   └── user_manual.md         # 用户手册
├── logs/                # 日志文件
│   ├── detection.log    # 检测日志
│   ├── error.log       # 错误日志
│   └── debug.log       # 调试日志
├── scripts/            # 脚本文件
│   ├── setup_db.py    # 数据库初始化
│   └── run_server.sh  # 服务器启动脚本
├── tests/             # 测试文件
│   ├── __init__.py
│   ├── test_auth.py   # 认证测试
│   ├── test_camera.py # 摄像头测试
│   ├── test_detection.py  # 检测测试
│   ├── test_history.py   # 历史查询测试
│   ├── test_plugins.py   # 插件测试
│   ├── test_statistics.py # 统计测试
│   └── test_violation.py # 违规测试
├── .gitignore         # Git忽略文件
├── README.md          # 项目说明
├── requirements.txt   # 依赖清单
└── run.py            # 应用入口
```

## 配置说明

1. **视频流配置**
   ```python
   VideoStreamConfig:
     MAX_WIDTH = 1280
     MAX_HEIGHT = 720
     JPEG_QUALITY = 80
     TARGET_FPS = 25
   ```

2. **检测模型配置**
   ```python
   MODEL_CONFIG:
     model_path = 'yolov8n.pt'
     tracker_type = 'botsort'
   ```

## 开发指南

1. **添加新功能**
   - 在routes/目录添加新路由
   - 在services/目录实现业务逻辑
   - 在models/目录定义数据模型

2. **插件开发**
   - plugin_template.py
   - 遵循插件接口规范
   - 详见插件开发指南

## 常见问题

1. **数据库连接失败**
   - 检查数据库配置
   - 确保MySQL服务运行

2. **视频流卡顿**
   - 调整视频流参数
   - 检查网络带宽

## 贡献指南

1. Fork 项目
2. 创建新分支
3. 提交更改
4. 发起 Pull Request

# PowerShell 脚本：一键运行所有测试并生成覆盖率报告
# 用法: .\scripts\run_tests.ps1 [选项]
# 选项:
#   -Quick      快速模式，不生成 HTML 报告
#   -Verbose    显示更详细的输出
#   -Failed     只重新运行失败的测试
#   -Open       测试完成后自动打开 HTML 报告

## 许可证

MIT License

## 联系方式

- 作者：[want-be-human]
- 邮箱：[798370740@qq.com]

## 致谢

感谢以下开源项目：
- Flask
- YOLOv8
- OpenCV
- 其他依赖库