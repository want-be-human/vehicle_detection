# 车辆检测系统测试文档

## 1. 测试概述

本文档描述了车辆检测系统的单元测试覆盖情况。测试目标是达到语句覆盖率和分支覆盖率均在80%以上。

### 1.1 测试框架

- **测试框架**: pytest
- **覆盖率工具**: pytest-cov
- **Mock工具**: unittest.mock
- **数据库**: SQLite (内存数据库，用于测试)

### 1.2 测试文件结构

```
tests/
├── conftest.py          # 测试配置和通用fixtures
├── test_auth.py         # 认证模块测试 (原有)
├── test_detection.py    # 检测模块测试 (原有)
├── test_violation.py    # 违规模块测试 (原有)
├── test_models.py       # 数据模型测试 (新增)
├── test_services.py     # 服务层测试 (新增)
├── test_routes.py       # 路由接口测试 (新增)
├── test_utils.py        # 工具类测试 (新增)
└── test_config.py       # 配置测试 (新增)
```

---

## 2. 测试模块详情

### 2.1 数据模型测试 (test_models.py)

测试所有数据库模型的创建、属性、方法和关联关系。

#### Camera 模型测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 创建测试 | `test_camera_creation` | 验证摄像头记录创建及所有字段正确性 |
| 默认值测试 | `test_camera_default_values` | 验证is_active和status默认值 |
| 字符串表示 | `test_camera_repr` | 验证__repr__方法输出 |
| 关联关系 | `test_camera_with_detections` | 验证与Detection的一对多关系 |

#### Detection 模型测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 创建测试 | `test_detection_creation` | 验证检测记录创建 |
| 默认值测试 | `test_detection_default_values` | 验证is_violation默认为False |
| 字符串表示 | `test_detection_repr` | 验证__repr__方法 |

#### Violation 模型测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 创建测试 | `test_violation_creation` | 验证违规记录创建 |
| to_dict方法 | `test_violation_to_dict` | 验证序列化输出 |
| 默认类型 | `test_violation_default_type` | 验证violation_type默认为'parking' |

#### User 模型测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 创建测试 | `test_user_creation` | 验证用户记录创建 |
| 默认角色 | `test_user_default_role` | 验证role默认为'user' |
| 唯一约束 | `test_user_unique_username` | 验证username唯一性约束 |

#### Statistics 模型测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 创建测试 | `test_statistics_creation` | 验证统计记录创建 |
| to_dict方法 | `test_statistics_to_dict` | 验证序列化输出 |
| 字符串表示 | `test_statistics_repr` | 验证__repr__方法 |
| 默认值 | `test_statistics_default_values` | 验证total_count默认为0 |

---

### 2.2 服务层测试 (test_services.py)

测试业务逻辑层的所有服务类。

#### AuthService 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 认证成功 | `test_authenticate_user_success` | 正确凭据返回token |
| 密码错误 | `test_authenticate_user_wrong_password` | 错误密码返回None |
| 用户不存在 | `test_authenticate_user_not_found` | 不存在用户返回None |
| 注册成功 | `test_register_user_success` | 验证用户注册 |
| JWT创建 | `test_create_jwt_token` | 验证JWT令牌生成 |

#### CameraService 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 数据验证成功 | `test_validate_camera_data_success` | 有效数据通过验证 |
| 缺少必填字段 | `test_validate_camera_data_missing_field` | 缺少字段抛出异常 |
| IP格式错误 | `test_validate_camera_data_invalid_ip` | 无效IP抛出异常 |
| 端口范围错误 | `test_validate_camera_data_invalid_port` | 无效端口抛出异常 |
| 连接测试成功 | `test_test_camera_connection_success` | 摄像头连接成功 |
| 连接打开失败 | `test_test_camera_connection_fail_open` | 连接打开失败 |
| 读取帧失败 | `test_test_camera_connection_fail_read` | 读取帧失败 |
| 添加摄像头成功 | `test_add_camera_success` | 添加摄像头成功 |
| 禁停区域格式错误 | `test_add_camera_invalid_restricted_areas` | 格式错误异常 |
| 删除摄像头 | `test_delete_camera_success` | 删除摄像头成功 |
| 更新禁停区域 | `test_update_restricted_areas_success` | 更新禁停区域 |
| 更新禁停区域失败 | `test_update_restricted_areas_invalid_format` | 格式错误异常 |

#### DetectionService 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 启动检测成功 | `test_start_detection_success` | 成功启动检测 |
| 重复启动 | `test_start_detection_duplicate` | 重复启动被拒绝 |
| 视频路径生成 | `test_get_video_path` | 验证路径格式 |
| 获取处理状态 | `test_get_processing_status` | 获取线程状态 |
| 获取所有检测 | `test_get_all_detections` | 获取检测记录 |

#### ViolationService 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 摄像头不存在 | `test_check_violations_no_camera` | 无效摄像头返回空 |
| 无禁停区域 | `test_check_violations_no_restricted_areas` | 无禁停区域返回空 |
| 获取违规记录空 | `test_get_violations_empty` | 空查询结果 |
| 带筛选条件 | `test_get_violations_with_filters` | 多条件筛选 |
| 违规缓存 | `test_violation_cache` | 防重复机制 |

#### StatisticsService 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 无数据统计 | `test_get_daily_statistics_no_data` | 无数据返回空统计 |
| 有数据统计 | `test_get_daily_statistics_with_data` | 有数据返回统计 |
| 按年查询 | `test_query_statistics_year` | 年度查询 |
| 按月查询 | `test_query_statistics_month` | 月度查询 |
| 按周查询 | `test_query_statistics_week` | 周查询 |
| 无效类型 | `test_query_statistics_invalid_type` | 无效类型返回None |
| 统计概要空 | `test_get_summary_empty` | 空概要 |
| 统计概要有数据 | `test_get_summary_with_data` | 有数据概要 |
| 图表生成 | `test_generate_charts` | 图表数据生成 |

#### HistoryService 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 查询未找到 | `test_query_video_not_found` | 未找到返回None |
| 查询找到 | `test_query_video_found` | 找到返回路径 |

---

### 2.3 路由接口测试 (test_routes.py)

测试所有REST API接口的请求和响应。

#### 连接测试路由
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 连接测试 | `test_connect_route` | GET /api/test 返回200 |

#### 认证路由 (/auth)
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 注册成功 | `test_register_success` | POST /auth/register 返回200 |
| 注册失败 | `test_register_failure` | 异常返回4xx |
| 登录成功 | `test_login_success` | POST /auth/login 返回token |
| 登录失败 | `test_login_failure` | 无效凭据返回401 |

#### 摄像头路由 (/camera)
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 添加成功 | `test_add_camera_success` | POST /cameras 返回201 |
| 添加失败 | `test_add_camera_failure` | 异常返回4xx |
| 删除成功 | `test_delete_camera_success` | DELETE /cameras/<id> 返回200 |
| 删除不存在 | `test_delete_camera_not_found` | 不存在返回4xx |

#### 检测路由 (/detection)
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 启动检测成功 | `test_start_detection_success` | POST /detect 返回200 |
| 带保存天数 | `test_start_detection_with_retention` | 自定义保存天数 |
| 获取检测记录 | `test_get_detections` | GET /detections |
| 获取处理状态 | `test_get_processing_status` | GET /status |
| 分析文件成功 | `test_analyze_file_success` | POST /analyze |
| 配置特殊车辆成功 | `test_configure_special_vehicles_success` | POST /special-vehicles/config |
| 配置特殊车辆失败 | `test_configure_special_vehicles_invalid` | 格式错误返回400 |
| 配置缺少字段 | `test_configure_special_vehicles_missing_fields` | 缺少字段返回400 |
| 配置视频流成功 | `test_configure_stream_success` | POST /stream/config |
| 视频流边界值 | `test_configure_stream_boundary_values` | 边界值限制 |

#### 违规路由 (/violation)
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 获取违规记录 | `test_get_violations_success` | GET /records 返回200 |
| 摄像头筛选 | `test_get_violations_with_camera_filter` | camera_id参数 |
| 时间筛选 | `test_get_violations_with_time_filter` | start_time/end_time参数 |
| 车辆类型筛选 | `test_get_violations_with_vehicle_type_filter` | vehicle_type参数 |
| 违规类型筛选 | `test_get_violations_with_violation_type_filter` | violation_type参数 |
| 时间格式错误 | `test_get_violations_invalid_time_format` | 格式错误返回400 |

#### 统计路由 (/statistics)
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 获取每日统计 | `test_get_daily_statistics` | GET /daily |
| 指定日期 | `test_get_daily_statistics_with_date` | date参数 |
| 查询统计成功 | `test_query_statistics_success` | POST /query |
| 查询无数据 | `test_query_statistics_no_data` | 无数据返回404 |
| 获取图表成功 | `test_get_charts_success` | GET /charts/<date> |
| 图表无数据 | `test_get_charts_no_data` | 无数据返回404 |
| 统计概要成功 | `test_get_summary_success` | GET /summary |
| 统计概要错误 | `test_get_summary_error` | 错误返回500 |

#### 历史路由 (/history)
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 查询成功 | `test_query_history_success` | POST /query 返回video_url |
| 查询未找到 | `test_query_history_not_found` | 未找到返回404 |

---

### 2.4 工具类测试 (test_utils.py)

测试各类工具函数和辅助类。

#### ViolationDetector 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 点在多边形内 | `test_is_point_in_polygon_inside` | 内部点返回True |
| 点在多边形外 | `test_is_point_in_polygon_outside` | 外部点返回False |
| 点在边界上 | `test_is_point_in_polygon_on_edge` | 边界情况 |
| 复杂多边形 | `test_is_point_in_polygon_complex` | L形多边形测试 |
| 空禁区列表 | `test_check_vehicle_violation_empty_areas` | 空列表返回[] |
| 无检测框 | `test_check_vehicle_violation_no_boxes` | boxes为None返回[] |
| 车辆在禁区 | `test_check_vehicle_violation_vehicle_in_area` | 检测到违规 |
| 车辆不在禁区 | `test_check_vehicle_violation_vehicle_outside_area` | 无违规 |
| 非车辆忽略 | `test_check_vehicle_violation_non_vehicle_ignored` | 忽略非车辆类别 |
| 多禁区检测 | `test_check_vehicle_violation_multiple_areas` | 多禁区场景 |
| 车辆类别配置 | `test_vehicle_classes` | 验证VEHICLE_CLASSES |

#### VideoStreamConfig 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 默认值 | `test_default_values` | 验证默认配置 |
| 配置修改 | `test_config_modification` | 验证配置可修改 |

#### WebSocket工具函数测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 发送违规提醒(有摄像头) | `test_emit_violation_alert_with_camera` | 指定房间发送 |
| 发送违规提醒(广播) | `test_emit_violation_alert_without_camera` | 全局广播 |
| 发送违规提醒(异常) | `test_emit_violation_alert_exception` | 异常处理 |
| 发送特殊车辆提醒 | `test_emit_special_vehicle_alert` | 特殊车辆通知 |
| 发送摄像头状态 | `test_emit_camera_status` | 状态更新 |
| 发送检测统计 | `test_emit_detection_stats` | 统计数据推送 |
| 发送视频帧 | `test_emit_video_frame` | 视频帧传输 |
| 发送视频帧(缩放) | `test_emit_video_frame_with_resize` | 需要缩放时 |
| 发送错误事件 | `test_emit_error` | 错误事件 |
| 发送流媒体状态 | `test_emit_streaming_status` | 流状态 |
| 发送流媒体结果 | `test_emit_streaming_result` | 流结果 |

#### YOLOIntegration 测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 模型不存在 | `test_init_invalid_model` | 抛出FileNotFoundError |
| 无效跟踪器 | `test_init_invalid_tracker` | 抛出ValueError |
| 自定义跟踪器无配置 | `test_init_custom_tracker_no_config` | 抛出ValueError |
| 初始化成功 | `test_init_success` | 正常初始化 |
| 自定义特殊车辆 | `test_init_with_custom_special_vehicles` | 自定义配置 |
| 目标类别 | `test_target_classes` | 验证TARGET_CLASSES |
| 默认特殊车辆 | `test_special_vehicles_default` | 验证SPECIAL_VEHICLES |
| 跟踪器选项 | `test_tracker_options` | 验证TRACKER_OPTIONS |

#### 日志配置测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 日志配置 | `test_setup_logger` | 验证logger配置 |
| 日志格式 | `test_log_format` | 验证LOG_FORMAT |
| 日志目录 | `test_log_directory` | 验证LOG_DIR |

---

### 2.5 配置测试 (test_config.py)

测试应用配置和初始化。

#### Config类测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 数据库URI | `test_config_database_uri` | 验证SQLALCHEMY_DATABASE_URI |
| 跟踪配置 | `test_config_track_modifications` | 验证SQLALCHEMY_TRACK_MODIFICATIONS |
| 基础目录 | `test_config_base_dir` | 验证BASE_DIR |
| 模型目录 | `test_config_model_dir` | 验证MODEL_DIR |
| 配置目录 | `test_config_config_dir` | 验证CONFIG_DIR |

#### 调度器配置测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 调度器存在 | `test_scheduler_exists` | 验证scheduler对象 |
| 调度器类型 | `test_scheduler_type` | 验证BackgroundScheduler类型 |

#### 应用初始化测试
| 测试项 | 测试方法 | 描述 |
|--------|----------|------|
| 创建应用 | `test_create_app` | 验证create_app函数 |
| 带配置创建 | `test_create_app_with_config` | 自定义配置 |
| 数据库初始化 | `test_db_initialized` | 验证db对象 |
| 蓝图注册 | `test_blueprints_registered` | 验证所有蓝图 |

---

## 3. 运行测试

### 3.1 运行全部测试

```bash
python scripts/run_tests.py
```

### 3.2 运行特定测试文件

```bash
python scripts/run_tests.py --tests-dir tests/test_models.py
```

### 3.3 快速模式（不生成HTML报告）

```bash
python scripts/run_tests.py --quick
```

### 3.4 详细输出

```bash
python scripts/run_tests.py --verbose
```

### 3.5 只运行失败的测试

```bash
python scripts/run_tests.py --failed
```

### 3.6 自动打开覆盖率报告

```bash
python scripts/run_tests.py --open
```

---

## 4. 覆盖率目标

| 模块 | 目标语句覆盖率 | 目标分支覆盖率 |
|------|---------------|---------------|
| models | ≥90% | ≥90% |
| services | ≥80% | ≥80% |
| routes | ≥85% | ≥85% |
| utils | ≥80% | ≥80% |
| config | ≥90% | ≥90% |
| **总计** | **≥80%** | **≥80%** |

---

## 5. 未测试模块说明

以下模块/文件由于特殊原因未包含在测试覆盖范围内：

1. **plugins_sercivve.py** - 文件名拼写错误，建议修复后添加测试
2. **image_processing.py** - 需要实际图像文件，建议使用mock
3. **camera_utils.py** - 依赖硬件设备
4. **plugin_loader.py** - 插件系统尚未完全实现
5. **example_plugin.py** - 示例插件，非核心功能

---

## 6. 测试维护建议

1. **新增功能时**: 同步添加对应测试用例
2. **修改功能时**: 更新相关测试确保覆盖
3. **代码审查时**: 检查测试覆盖率变化
4. **持续集成**: 将测试集成到CI/CD流程

---

## 7. 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2025-12-28 | 初始版本，新增完整测试套件 |
