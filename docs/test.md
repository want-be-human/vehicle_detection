# 安全测试实验报告

## 一、实验基本信息

| 项目 | 内容 |
|------|------|
| 实验名称 | 安全测试实验 |
| 实验课程 | Software Testing |
| 实验对象 | Vehicle Detection（车辆检测系统） |
| 项目地址 | https://github.com/want-be-human/vehicle_detection |
| 小组成员 | 【人工填写部分】 |
| 实验日期 | 2025年12月29日 |

---

## 二、实验环境

| 环境项 | 配置详情 |
|--------|----------|
| 操作系统 | Windows 11 |
| 编程语言与版本 | Python 3.12.7 |
| 测试框架 | Pytest 7.4.4 |
| 覆盖率工具 | pytest-cov 7.0.0 |
| 项目构建方式 | pip + requirements.txt |
| 数据库 | SQLite (测试环境) / MySQL (生产环境) |
| 主要依赖 | Flask 3.1.2, SQLAlchemy 2.0.45, ultralytics 8.3.241, PyJWT |

### 测试运行环境配置

**环境配置命令：**
```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v
```

**依赖文件 `requirements.txt` 关键内容：**
```txt
Flask==3.1.2
SQLAlchemy==2.0.45
pytest==7.4.4
pytest-cov==7.0.0
PyJWT>=2.0.0
ultralytics>=8.0.0
flask-socketio>=5.0.0
```

---

## 三、实验内容与方法

### 3.1 项目选择

**项目简介**：Vehicle Detection是一个基于Python Flask的车辆检测与管理系统，使用YOLO模型进行实时车辆检测，支持违规行为识别、特殊车辆监控等功能。

**选择理由**：
1. 项目涉及安全敏感功能（用户认证、权限管理）
2. 包含复杂的业务逻辑（视频流处理、违规检测）
3. 代码结构清晰，采用分层架构（routes/services/models）
4. 已有基础测试用例，便于扩展和分析

**项目架构**：
```
vehicle_detection/
├── app/
│   ├── routes/          # 路由层（API接口）
│   ├── services/        # 服务层（业务逻辑）
│   ├── models/          # 数据模型层
│   ├── utils/           # 工具类
│   └── config/          # 配置文件
├── tests/               # 测试用例
└── scripts/             # 脚本工具
```

### 3.2 测试用例执行

**运行方式**：
```bash
# 运行所有测试并生成覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 运行并自动打开HTML报告
python scripts/run_tests.py --open

# 仅运行特定测试文件
pytest tests/test_auth.py -v

# 运行安全审计测试（失败用例）
pytest tests/test_security_audit.py -v
```

**测试文件组织**：
| 测试文件 | 测试内容 | 用例数量 |
|----------|----------|----------|
| test_auth.py | 用户认证相关测试（注册、登录、JWT） | 38 |
| test_config.py | 配置文件测试 | 8 |
| test_detection.py | 车辆检测服务测试 | 15 |
| test_models.py | 数据模型测试 | 43 |
| test_routes.py | API路由测试 | 68 |
| test_services.py | 服务层测试 | 82 |
| test_utils.py | 工具类测试 | 45 |
| test_violation.py | 违规检测测试 | 25 |
| **test_security_audit.py** | **安全审计测试（失败用例）** | **4** |

### 3.3 覆盖率计算

**工具配置**：使用pytest-cov插件，配置文件为pytest.ini

**pytest.ini 配置内容：**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=app --cov-branch --cov-report=term-missing --cov-report=html
```

**覆盖率类型**：
- **语句覆盖率（Statement Coverage）**：衡量代码行被执行的比例
- **分支覆盖率（Branch Coverage）**：衡量条件分支被覆盖的比例

**计算命令**：
```bash
pytest --cov=app --cov-branch tests/ --cov-report=html --cov-report=xml
```

### 3.4 缺陷分析方法

**缺陷定位流程**：
1. **运行测试**：执行pytest获取失败用例列表
2. **分析错误信息**：查看堆栈跟踪和断言失败详情
3. **代码审查**：定位相关源代码文件和行号
4. **根因分析**：分析代码逻辑，确定缺陷根本原因
5. **修复验证**：提出修复方案并验证

---

## 四、测试结果

### 4.1 测试用例执行结果

| 指标 | 数值 |
|------|------|
| 总测试用例数 | 328 |
| 通过数 | 324 |
| **失败数** | **4** |
| 跳过数 | 0 |
| 通过率 | 98.78% |

**测试执行输出**：
```
================================================================================= test session starts ==================================================================================
platform win32 -- Python 3.12.7, pytest-7.4.4, pluggy-1.6.0
rootdir: D:\vehicle_detection
configfile: pytest.ini
plugins: anyio-4.2.0, cov-7.0.0, stub-1.1.0
collected 328 items

tests/test_auth.py ......................................                                                       [ 11%]
tests/test_config.py ........                                                                                   [ 14%]
tests/test_detection.py ...............                                                                         [ 18%]
tests/test_models.py ...........................................                                                [ 31%]
tests/test_routes.py ....................................................................                        [ 52%]
tests/test_security_audit.py FFFF                                                                               [ 53%]
tests/test_services.py ..................................................................................       [ 78%]
tests/test_utils.py .............................................                                               [ 92%]
tests/test_violation.py .........................                                                               [100%]

=========================== short test summary info ===========================
FAILED tests/test_security_audit.py::TestSecurityAudit::test_jwt_secret_key_not_hardcoded
FAILED tests/test_security_audit.py::TestSecurityAudit::test_password_minimum_length_validation
FAILED tests/test_security_audit.py::TestSecurityAudit::test_camera_delete_requires_authentication
FAILED tests/test_security_audit.py::TestSecurityAudit::test_password_must_contain_special_characters
================== 4 failed, 324 passed, 1 warning in 10.86s ==================
```

【人工附上截图：pytest运行结果截图】

### 4.2 覆盖率数据

#### 总体覆盖率
| 覆盖率类型 | 百分比 |
|------------|--------|
| 语句覆盖率（Statement Coverage） | **81.63%** |
| 分支覆盖率（Branch Coverage） | **62.27%** |

#### 各模块详细覆盖率

| 模块 | 语句覆盖率 | 分支覆盖率 |
|------|------------|------------|
| app/__init__.py | 100.00% | 100.00% |
| config/config.py | 100.00% | 100.00% |
| models/camera.py | 100.00% | 100.00% |
| models/detection.py | 100.00% | 100.00% |
| models/user.py | 100.00% | 100.00% |
| models/violation.py | 100.00% | 100.00% |
| routes/auth.py | 100.00% | 100.00% |
| routes/camera.py | 100.00% | 100.00% |
| routes/detection.py | 96.49% | 100.00% |
| routes/violation.py | 100.00% | 100.00% |
| services/auth_service.py | 100.00% | 100.00% |
| services/camera_service.py | 87.61% | 86.11% |
| services/detection_service.py | 60.34% | 20.45% |
| services/violation_service.py | 100.00% | 95.00% |
| services/statistics_service.py | 70.34% | 46.88% |
| utils/websocket_utils.py | 83.10% | 100.00% |
| utils/yolo_integration.py | 47.52% | 25.00% |

【人工附上截图：htmlcov/index.html 覆盖率报告截图】

### 4.3 失败用例统计

| 序号 | 测试用例名称 | 缺陷描述 | 严重等级 |
|------|--------------|----------|----------|
| 1 | test_jwt_secret_key_not_hardcoded | JWT密钥硬编码在源代码中 | Critical |
| 2 | test_password_minimum_length_validation | 弱密码可以注册成功 | High |
| 3 | test_camera_delete_requires_authentication | 删除摄像头接口无权限验证 | High |
| 4 | test_password_must_contain_special_characters | 密码无特殊字符要求 | Medium |

---

## 五、缺陷分析与根因定位

### 5.1 失败用例详细分析

---

#### 缺陷1：JWT密钥硬编码（Critical）

**测试文件**：`tests/test_security_audit.py`

**测试用例代码**：
```python
def test_jwt_secret_key_not_hardcoded(self):
    """
    测试1：JWT密钥不应硬编码
    
    安全要求：JWT密钥应从环境变量或安全配置中读取，
    不应在源代码中硬编码默认值。
    
    CWE-798: Use of Hard-coded Credentials
    """
    from app.services.auth_service import SECRET_KEY
    
    # 定义不安全的硬编码密钥列表
    insecure_keys = [
        'your_secret_key',
        'secret',
        'secret_key', 
        'key',
        '123456',
        'password',
        'admin',
        'test'
    ]
    
    # 断言：密钥不应该是这些不安全的值
    assert SECRET_KEY not in insecure_keys, \
        f"安全漏洞: 发现硬编码的不安全密钥 '{SECRET_KEY}'，应使用环境变量配置"
```

**测试失败输出**：
```
FAILED tests/test_security_audit.py::TestSecurityAudit::test_jwt_secret_key_not_hardcoded
E   AssertionError: 安全漏洞: 发现硬编码的不安全密钥 'your_secret_key'，应使用环境变量配置
E   assert 'your_secret_key' not in ['your_secret_key', 'secret', 'secret_key', 'key', '123456', 'password', ...]
```

【人工附上截图：test_jwt_secret_key_not_hardcoded 失败输出截图】

**定位过程**：

1. **运行测试**：执行 `pytest tests/test_security_audit.py::TestSecurityAudit::test_jwt_secret_key_not_hardcoded -v`
2. **分析错误信息**：断言失败，提示密钥值为 `your_secret_key`
3. **代码定位**：查看 `app/services/auth_service.py` 文件

**缺陷代码位置**：`app/services/auth_service.py` 第11行

```python
"""
用户认证服务
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db
import jwt
import datetime

SECRET_KEY = 'your_secret_key'  # <-- 缺陷位置：硬编码密钥

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = create_jwt_token(user)
        return True, token
    return False, None
```

**根因分析**：
- 开发者在开发阶段使用占位符密钥，未在生产环境替换
- 缺乏配置管理机制，未使用环境变量或配置文件
- 违反安全编码规范：**CWE-798（硬编码凭证）**

**修复建议**：
```python
import os

# 从环境变量读取密钥，如果未设置则生成随机密钥
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
if not SECRET_KEY:
    import secrets
    SECRET_KEY = secrets.token_hex(32)
    print("Warning: JWT_SECRET_KEY not set, using random key")
```

---

#### 缺陷2：密码最小长度验证缺失（High）

**测试文件**：`tests/test_security_audit.py`

**测试用例代码**：
```python
def test_password_minimum_length_validation(self, db_session):
    """
    测试2：密码最小长度验证
    
    安全要求：系统应拒绝长度小于8位的密码。
    
    OWASP: Authentication - Password Strength Requirements
    """
    from app.services.auth_service import register_user
    
    weak_password = "123"  # 只有3位的弱密码
    
    # 期望：注册应该抛出异常或返回错误
    try:
        user = register_user("test_weak_pwd_user", weak_password, "user")
        # 如果没有抛出异常，检查是否返回了错误
        assert user is None, \
            f"安全漏洞: 弱密码 '{weak_password}' (长度={len(weak_password)}) 不应被接受，但注册成功了"
    except ValueError as e:
        # 期望抛出密码强度验证异常
        pass
    finally:
        db_session.session.rollback()
```

**测试失败输出**：
```
FAILED tests/test_security_audit.py::TestSecurityAudit::test_password_minimum_length_validation
E   AssertionError: 安全漏洞: 弱密码 '123' (长度=3) 不应被接受，但注册成功了
E   assert <User 1> is None
```

【人工附上截图：test_password_minimum_length_validation 失败输出截图】

**定位过程**：

1. **运行测试**：执行安全测试，发现弱密码可以成功注册
2. **分析错误信息**：用户对象被成功创建，说明没有密码验证
3. **代码定位**：查看 `app/services/auth_service.py` 的 `register_user` 函数

**缺陷代码位置**：`app/services/auth_service.py` 第26-31行

```python
def register_user(username, password, role):
    # 缺少密码强度验证！
    hashed_password = generate_password_hash(password)  # 直接哈希，无验证
    user = User(username=username, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return user
```

**根因分析**：
- `register_user` 函数直接接受任意长度的密码
- 缺乏输入验证层
- 违反 **OWASP 密码强度要求**：密码应至少8位

**修复建议**：
```python
def validate_password_strength(password):
    """验证密码强度"""
    if len(password) < 8:
        raise ValueError("密码长度至少8位")
    return True

def register_user(username, password, role):
    # 添加密码强度验证
    validate_password_strength(password)
    
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return user
```

---

#### 缺陷3：API接口缺少认证保护（High）

**测试文件**：`tests/test_security_audit.py`

**测试用例代码**：
```python
def test_camera_delete_requires_authentication(self, client, db_session):
    """
    测试3：删除摄像头需要身份认证
    
    安全要求：敏感操作（如删除资源）必须验证用户身份。
    未认证的请求应返回401状态码。
    
    OWASP: Broken Access Control
    """
    from app.models.camera import Camera
    
    # 先创建一个测试摄像头
    camera = Camera(
        name='Test Camera',
        ip_address='192.168.1.100',
        port=554,
        url='rtsp://test',
        resolution='1920x1080',
        frame_rate=30,
        encoding_format='H.264'
    )
    db_session.session.add(camera)
    db_session.session.commit()
    camera_id = camera.id
    
    # 不携带任何认证信息，直接调用删除接口
    response = client.delete(f"/camera/cameras/{camera_id}")
    
    # 期望：应返回401未授权
    assert response.status_code == 401, \
        f"安全漏洞: 删除摄像头API缺少认证保护，未认证请求返回了 {response.status_code} 而不是 401"
```

**测试失败输出**：
```
FAILED tests/test_security_audit.py::TestSecurityAudit::test_camera_delete_requires_authentication
E   AssertionError: 安全漏洞: 删除摄像头API缺少认证保护，未认证请求返回了 200 而不是 401
E   assert 200 == 401
E    +  where 200 = <WrapperTestResponse streamed [200 OK]>.status_code
```

【人工附上截图：test_camera_delete_requires_authentication 失败输出截图】

**定位过程**：

1. **运行测试**：未携带认证信息调用DELETE接口
2. **分析错误信息**：接口返回200成功，而非401未授权
3. **代码定位**：查看 `app/routes/camera.py` 的路由定义

**缺陷代码位置**：`app/routes/camera.py` 第87-93行

```python
@camera_blueprint.route('/cameras/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    """
    删除摄像头接口
    """
    # 缺少认证装饰器！任何人都可以调用
    CameraService.delete_camera(camera_id)
    return jsonify({"message": "Camera deleted successfully"}), 200
```

**根因分析**：
- 删除路由未添加 `@jwt_required()` 或类似的认证装饰器
- 任何未认证用户都可以删除任意摄像头
- 违反 **OWASP A01:2021 – Broken Access Control**

**修复建议**：
```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@camera_blueprint.route('/cameras/<int:camera_id>', methods=['DELETE'])
@jwt_required()  # 添加认证要求
def delete_camera(camera_id):
    """
    删除摄像头接口 - 需要管理员权限
    """
    current_user = get_jwt_identity()
    # 可选：检查用户角色
    # if current_user['role'] != 'admin':
    #     return jsonify({"error": "Permission denied"}), 403
    
    CameraService.delete_camera(camera_id)
    return jsonify({"message": "Camera deleted successfully"}), 200
```

---

#### 缺陷4：密码特殊字符验证缺失（Medium）

**测试文件**：`tests/test_security_audit.py`

**测试用例代码**：
```python
def test_password_must_contain_special_characters(self, db_session):
    """
    测试4：密码必须包含特殊字符
    
    安全要求：密码应包含特殊字符以增强安全性。
    纯数字或纯字母密码应被拒绝。
    
    NIST SP 800-63B: Digital Identity Guidelines
    """
    from app.services.auth_service import register_user
    
    # 测试纯字母数字密码（无特殊字符）
    simple_password = "abcd1234"  # 8位但无特殊字符
    
    try:
        user = register_user("test_simple_pwd_user", simple_password, "user")
        # 如果成功注册，说明没有特殊字符验证
        assert user is None, \
            f"安全漏洞: 密码 '{simple_password}' 不包含特殊字符，不应被接受"
    except ValueError as e:
        # 期望抛出密码强度验证异常
        assert "特殊字符" in str(e) or "special" in str(e).lower()
    finally:
        db_session.session.rollback()
```

**测试失败输出**：
```
FAILED tests/test_security_audit.py::TestSecurityAudit::test_password_must_contain_special_characters
E   AssertionError: 安全漏洞: 密码 'abcd1234' 不包含特殊字符，不应被接受
E   assert <User 1> is None
```

【人工附上截图：test_password_must_contain_special_characters 失败输出截图】

**定位过程**：

1. **运行测试**：使用纯字母数字密码尝试注册
2. **分析错误信息**：用户成功创建，说明无密码复杂度要求
3. **代码定位**：同缺陷2，`register_user` 函数缺少验证

**缺陷代码位置**：`app/services/auth_service.py` 第26-31行（同缺陷2）

**根因分析**：
- 密码验证完全缺失
- 不符合 **NIST SP 800-63B** 数字身份指南要求
- 纯字母数字密码易被暴力破解

**修复建议**：
```python
import re

def validate_password_strength(password):
    """验证密码强度 - 完整版"""
    if len(password) < 8:
        raise ValueError("密码长度至少8位")
    if not re.search(r'[A-Z]', password):
        raise ValueError("密码需包含大写字母")
    if not re.search(r'[a-z]', password):
        raise ValueError("密码需包含小写字母")
    if not re.search(r'\d', password):
        raise ValueError("密码需包含数字")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("密码需包含特殊字符")
    return True
```

---

### 5.2 缺陷根因总结

| 缺陷类型 | 数量 | 典型案例 | 改进措施 |
|----------|------|----------|----------|
| **安全配置缺陷** | 1 | 硬编码JWT密钥 | 使用环境变量或安全配置管理 |
| **权限控制缺陷** | 1 | API无认证 | 实现统一认证中间件 |
| **输入验证缺陷** | 2 | 密码强度验证缺失 | 添加输入验证层 |

**缺陷严重等级分布**：

```
Critical (严重)  ████████░░  25% (1个)
High (高)        ████████████████░░  50% (2个)
Medium (中)      ████████░░  25% (1个)
```

---

## 六、总结与建议

### 6.1 实验总结

**实验收获**：
1. **测试工具使用**：熟练掌握了pytest和pytest-cov的使用，了解了覆盖率报告的解读方法
2. **安全测试思维**：学会从攻击者角度思考系统漏洞，设计针对性测试用例
3. **缺陷定位能力**：通过堆栈跟踪和代码审查快速定位问题根因
4. **代码审计经验**：识别常见安全反模式（硬编码凭证、缺少认证等）

**实验难点**：
1. **Mock技术应用**：需要模拟数据库、外部服务等依赖
2. **异步代码测试**：视频流处理涉及多线程，测试较复杂
3. **分支覆盖提升**：部分异常处理分支难以触发（如网络中断）
4. **安全测试设计**：需要安全知识储备才能设计有效的攻击测试

### 6.2 项目安全性建议

#### 高优先级（必须修复）
1. **密钥管理**
   - 使用环境变量存储敏感配置
   - 实现密钥轮换机制
   - 生产环境使用HSM或密钥管理服务

2. **身份认证加固**
   - 所有敏感API添加JWT认证
   - 实现基于角色的访问控制（RBAC）
   - 添加登录失败锁定机制

3. **输入验证**
   - 实现密码强度策略
   - 添加参数化查询防止SQL注入
   - 对所有用户输入进行验证和转义

#### 中优先级（建议修复）
4. **日志安全**
   - 脱敏处理敏感信息
   - 记录安全相关事件（登录失败、权限拒绝）
   - 实现日志完整性保护

5. **错误处理**
   - 统一错误响应格式
   - 隐藏技术细节和堆栈信息
   - 区分开发和生产环境的错误详情

6. **会话管理**
   - 实现Token刷新机制
   - 添加会话超时处理
   - 支持主动注销功能

### 6.3 测试方法改进建议

#### 覆盖率提升
1. **detection_service.py**（当前60.34%）
   - 添加视频流处理的集成测试
   - Mock YOLO模型进行单元测试
   - 覆盖异常处理分支

2. **yolo_integration.py**（当前47.52%）
   - 使用测试视频文件进行端到端测试
   - 模拟检测结果进行逻辑测试

#### 测试类型扩展
| 测试类型 | 当前状态 | 建议 |
|----------|----------|------|
| 单元测试 | ✅ 完善 | 继续维护 |
| 集成测试 | ⚠️ 部分 | 增加API集成测试 |
| 安全测试 | ⚠️ 不足 | 添加OWASP Top 10测试 |
| 性能测试 | ❌ 缺失 | 添加负载测试 |
| 模糊测试 | ❌ 缺失 | 使用Hypothesis库 |

---

## 附录

### A. 测试命令参考

```bash
# 运行所有测试
pytest tests/ -v

# 运行安全审计测试（会失败的用例）
pytest tests/test_security_audit.py -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html tests/

# 运行失败的测试
pytest --lf

# 显示最慢的10个测试
pytest --durations=10
```

### B. 覆盖率报告位置

- HTML报告：`htmlcov/index.html`
- XML报告：`coverage.xml`
- 文本摘要：`coverage_summary.txt`

### C. 安全测试用例文件

**文件路径**：`tests/test_security_audit.py`

```python
"""
安全审计测试用例

这些测试用例用于发现系统中的安全缺陷。
预期这些测试会失败，从而暴露潜在的安全问题。
"""

import pytest
from unittest.mock import patch, MagicMock


class TestSecurityAudit:
    """安全审计测试类 - 用于发现系统安全漏洞"""
    
    def test_jwt_secret_key_not_hardcoded(self):
        """测试1：JWT密钥不应硬编码"""
        # ... 完整代码见 tests/test_security_audit.py
    
    def test_password_minimum_length_validation(self, db_session):
        """测试2：密码最小长度验证"""
        # ... 完整代码见 tests/test_security_audit.py
    
    def test_camera_delete_requires_authentication(self, client, db_session):
        """测试3：删除摄像头需要身份认证"""
        # ... 完整代码见 tests/test_security_audit.py
    
    def test_password_must_contain_special_characters(self, db_session):
        """测试4：密码必须包含特殊字符"""
        # ... 完整代码见 tests/test_security_audit.py
```

### D. 参考资料

1. OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
2. CWE-798 硬编码凭证: https://cwe.mitre.org/data/definitions/798.html
3. NIST SP 800-63B 数字身份指南: https://pages.nist.gov/800-63-3/sp800-63b.html
4. Pytest Documentation: https://docs.pytest.org/

---

**报告完成日期**：2025年12月29日

**审核人**：【人工填写部分】
