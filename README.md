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
- **目标检测**: YOLOv8
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
│   ├── models/            # 数据模型
│   ├── routes/            # API路由
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── plugins/           # 插件系统
└── docs/                  # 项目文档
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