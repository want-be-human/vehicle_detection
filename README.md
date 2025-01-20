# vehicle-detection-system/

## 目录结构
```plaintext
vehicle-detection-system/
│
├── app/                          # Flask应用代码
│   ├── __init__.py               # Flask应用初始化
│   ├── models/                   # 数据库模型
│   │   ├── user.py               # 用户模型
│   │   ├── detection.py          # 车辆检测记录模型
│   │   ├── camera.py             # 摄像头管理模型
│   │   ├── alert.py              # 提醒记录模型
│   │   └── violation.py          # 违规记录模型
│   ├── routes/                   # Flask路由（API接口）
│   │   ├── auth.py               # 用户认证相关接口
│   │   ├── camera.py             # 摄像头管理接口
│   │   ├── detection.py          # 车辆检测相关接口
│   │   ├── alert.py              # 提醒管理接口
│   │   ├── violation.py          # 违规管理接口
│   │   ├── history.py            # 历史监控查询接口
│   │   ├── statistics.py         # 车辆统计接口
│   │   └── plugins.py            # 插件管理接口
│   ├── services/                 # 业务逻辑
│   │   ├── auth_service.py       # 用户认证服务
│   │   ├── camera_service.py     # 摄像头管理服务
│   │   ├── detection_service.py  # 车辆检测服务
│   │   ├── alert_service.py      # 提醒管理服务
│   │   ├── violation_service.py  # 违规管理服务
│   │   ├── history_service.py    # 历史监控查询服务
│   │   ├── statistics_service.py # 车辆统计服务
│   │   └── plugin_service.py     # 插件管理服务
│   ├── utils/                    # 工具函数
│   │   ├── image_processing.py   # 图像处理工具
│   │   ├── yolo_integration.py   # YOLO算法集成
│   │   ├── logging_utils.py      # 日志工具
│   │   ├── plugin_loader.py      # 插件加载工具
│   │   ├── camera_utils.py       # 摄像头管理工具
│   │   ├── alert_utils.py        # 提醒工具
│   │   └── violation_utils.py    # 违规检测工具
│   ├── plugins/                  # 插件目录
│   │   ├── __init__.py           # 插件初始化
│   │   ├── example_plugin.py     # 示例插件
│   │   └── plugin_template.py    # 插件模板
│   ├── config.py                 # 配置文件
│   └── logging_config.py         # 日志配置文件
│   └── assets/                   # 静态资源目录（新增）
│       ├── models/               # 存放模型文件
│       │   ├── yolov11.pt        # YOLO 模型文件
│       │   └── custom_model.pt   # 其他自定义模型文件
│       └── configs/              # 存放算法配置文件
│           ├── yolov11.yaml      # YOLO 配置文件
│           └── custom_config.yaml # 其他自定义配置文件
│
├── tests/                        # 单元测试
│   ├── test_auth.py              # 用户认证测试
│   ├── test_camera.py            # 摄像头管理测试
│   ├── test_detection.py         # 车辆检测测试
│   ├── test_alert.py             # 提醒管理测试
│   ├── test_violation.py         # 违规管理测试
│   ├── test_history.py           # 历史监控查询测试
│   ├── test_statistics.py        # 车辆统计测试
│   └── test_plugins.py           # 插件管理测试
│
├── migrations/                   # 数据库迁移文件（使用Alembic或Flask-Migrate）
│
├── static/                       # 静态文件（如图片、CSS、JS）
│   └── uploads/                  # 用户上传的图像文件
│
├── templates/                    # Flask模板文件（如果有前端页面）
│
├── requirements.txt              # 项目依赖包
│
├── README.md                     # 项目说明文档
│
├── docs/                         # 项目文档
│   ├── api_documentation.md      # API接口文档
│   ├── user_manual.md            # 用户手册
│   └── plugin_development_guide.md # 插件开发指南
│
├── scripts/                      # 脚本文件
│   ├── run_server.sh             # 启动服务器的脚本
│   └── setup_db.sh               # 初始化数据库的脚本
│
├── logs/                         # 日志文件目录
│   ├── app.log                   # 应用日志
│   └── detection.log             # 车辆检测日志
│
└── .gitignore                    # Git忽略文件
```
## 说明

## 项目结构说明

### 1. app/ 目录
这是后端 Flask 应用的核心代码目录，负责实现车辆管理系统的所有功能。

#### 1.1 __init__.py
- **功能**: Flask 应用的初始化文件。
- **职责**:
  - 初始化 Flask 应用。
  - 配置数据库连接。
  - 注册蓝图（API 路由）。

#### 1.2 models/ 目录
- **功能**: 定义数据库模型，用于与数据库交互。
- **文件**:
  - user.py: 用户模型，管理用户信息（如用户名、密码、权限等）。
  - detection.py: 车辆检测记录模型，存储检测结果（如车辆类型、位置、时间等）。
  - camera.py: 摄像头管理模型，存储摄像头信息（如摄像头 ID、位置、状态等）。
  - alert.py: 提醒记录模型，存储特殊车辆的提醒信息（如车辆类型、位置、时间等）。
  - violation.py: 违规记录模型，存储违规车辆的信息（如违规类型、位置、时间等）。

#### 1.3 routes/ 目录
- **功能**: 定义 Flask 的 API 路由，提供前端调用的接口。
- **文件**:
  - auth.py: 用户认证相关接口（如登录、注册、权限验证）。
  - camera.py: 摄像头管理接口（如摄像头增删、状态查询）。
  - detection.py: 车辆检测相关接口（如实时检测、特殊车辆标记）。
  - alert.py: 提醒管理接口（如提醒记录查询、提醒触发）。
  - violation.py: 违规管理接口（如违规记录查询、违规检测）。
  - history.py: 历史监控查询接口（如按时间查询历史记录）。
  - statistics.py: 车辆统计接口（如获取当天车辆统计数据）。
  - plugins.py: 插件管理接口（如插件加载、卸载）。

#### 1.4 services/ 目录
- **功能**: 实现业务逻辑，处理路由层传递的请求。
- **文件**:
  - auth_service.py: 用户认证服务（如验证用户身份、生成 Token）。
  - camera_service.py: 摄像头管理服务（如摄像头增删、状态更新）。
  - detection_service.py: 车辆检测服务（如实时检测、特殊车辆标记、结果存储）。
  - alert_service.py: 提醒管理服务（如触发提醒、记录提醒信息）。
  - violation_service.py: 违规管理服务（如检测违规行为、记录违规信息）。
  - history_service.py: 历史监控查询服务（如查询历史记录）。
  - statistics_service.py: 车辆统计服务（如统计当天车辆数据、生成图表数据）。
  - plugin_service.py: 插件管理服务（如插件加载、卸载、调用）。

#### 1.5 utils/ 目录
- **功能**: 提供工具函数，辅助业务逻辑的实现。
- **文件**:
  - image_processing.py: 图像处理工具（如图像裁剪、缩放、格式转换）。
  - yolo_integration.py: YOLO 算法集成工具（如加载模型、运行检测）。
  - logging_utils.py: 日志工具（如记录操作日志、错误日志）。
  - plugin_loader.py: 插件加载工具（如动态加载插件）。
  - camera_utils.py: 摄像头管理工具（如摄像头配置、状态检查）。
  - alert_utils.py: 提醒工具（如触发弹窗提醒、发声提醒）。
  - violation_utils.py: 违规检测工具（如检测逆行、禁停区域）。

#### 1.6 plugins/ 目录
- **功能**: 存放插件代码，支持功能扩展。
- **文件**:
  - __init__.py: 插件初始化文件。
  - example_plugin.py: 示例插件，展示插件开发规范。
  - plugin_template.py: 插件开发模板，便于开发者快速创建新插件。

#### 1.7 config.py
- **功能**: 配置文件，存储应用的配置信息。
- **职责**:
  - 数据库连接配置。
  - 日志配置。
  - 摄像头配置。
  - 算法模型路径配置。

#### 1.8 logging_config.py
- **功能**: 日志配置文件，定义日志格式、存储路径和日志级别。
- **职责**:
  - 配置日志输出格式。
  - 指定日志存储路径。
  - 设置日志级别（如 INFO、ERROR）。

### 2. tests/ 目录
- **功能**: 存放单元测试代码，确保各模块功能的正确性。
- **文件**:
  - test_auth.py: 用户认证模块的单元测试。
  - test_camera.py: 摄像头管理模块的单元测试。
  - test_detection.py: 车辆检测模块的单元测试。
  - test_alert.py: 提醒管理模块的单元测试。
  - test_violation.py: 违规管理模块的单元测试。
  - test_history.py: 历史监控查询模块的单元测试。
  - test_statistics.py: 车辆统计模块的单元测试。
  - test_plugins.py: 插件管理模块的单元测试。

### 3. migrations/ 目录
- **功能**: 存放数据库迁移文件，用于管理数据库结构的变更。
- **职责**:
  - 使用 Alembic 或 Flask-Migrate 生成迁移脚本。
  - 执行数据库迁移操作（如创建表、修改表结构）。

### 4. static/ 目录
- **功能**: 存放静态文件，供前端调用。
- **子目录**:
  - uploads/: 用户上传的图像文件。

### 5. templates/ 目录
- **功能**: 存放 Flask 模板文件（如果有前端页面）。
- **职责**:
  - 提供 HTML 模板，用于渲染前端页面。

### 6. requirements.txt
- **功能**: 列出项目所需的 Python 依赖包。
- **职责**:
  - 使用 `pip install -r requirements.txt` 安装依赖。

### 7. README.md
- **功能**: 项目说明文档。
- **职责**:
  - 介绍项目背景、功能、使用方法。
  - 提供项目启动指南。

### 8. docs/ 目录
- **功能**: 存放项目文档。
- **文件**:
  - api_documentation.md: API 接口文档，描述所有开放的 API 接口及其使用方法。
  - user_manual.md: 用户手册，指导用户如何使用系统。
  - plugin_development_guide.md: 插件开发指南，说明如何开发、加载和使用插件。

### 9. scripts/ 目录
- **功能**: 存放脚本文件，用于自动化任务。
- **文件**:
  - run_server.sh: 启动服务器的脚本。
  - setup_db.sh: 初始化数据库的脚本。

### 10. logs/ 目录
- **功能**: 存放日志文件。
- **文件**:
  - app.log: 应用日志，记录系统运行信息。
  - detection.log: 车辆检测日志，记录检测过程中的详细信息。
