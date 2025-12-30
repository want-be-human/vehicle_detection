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


class TestInputValidation:
    """输入验证测试类 - 用于发现输入验证缺陷"""
    
    def test_username_length_validation(self, db_session):
        """
        测试5：用户名长度验证
        
        安全要求：用户名应有最小和最大长度限制。
        过短或过长的用户名应被拒绝。
        
        CWE-20: Improper Input Validation
        """
        from app.services.auth_service import register_user
        
        # 测试单字符用户名
        short_username = "a"
        
        try:
            user = register_user(short_username, "ValidPass123!", "user")
            assert user is None, \
                f"输入验证缺陷: 过短的用户名 '{short_username}' (长度={len(short_username)}) 不应被接受"
        except ValueError as e:
            # 期望抛出用户名长度验证异常
            assert "用户名" in str(e) or "username" in str(e).lower()
        finally:
            db_session.session.rollback()
    
    def test_register_duplicate_username_returns_proper_error(self, client, db_session):
        """
        测试6：重复用户名注册应返回友好错误
        
        安全要求：当用户名已存在时，应返回400错误码和友好提示，
        而不是500服务器内部错误或暴露数据库错误信息。
        
        CWE-209: Generation of Error Message Containing Sensitive Information
        """
        from app.services.auth_service import register_user
        
        # 先注册一个用户
        register_user("duplicate_test_user", "Password123!", "user")
        db_session.session.commit()
        
        # 尝试用相同用户名再次注册 - 捕获异常来检查错误处理
        try:
            response = client.post('/auth/register', json={
                'username': 'duplicate_test_user',
                'password': 'AnotherPass456!',
                'role': 'user'
            })
            
            # 如果没有异常，检查状态码
            assert response.status_code == 400, \
                f"错误处理缺陷: 重复用户名应返回400，但返回了 {response.status_code}"
        except Exception as e:
            # 如果抛出异常到测试层，说明路由层没有正确处理异常
            error_msg = str(e).lower()
            assert False, \
                f"错误处理缺陷: 重复用户名注册导致未处理的异常暴露到客户端 - {type(e).__name__}: 系统应返回友好的400错误而非抛出异常"


class TestRateLimiting:
    """速率限制测试类 - 用于发现防暴力破解缺陷"""
    
    def test_login_rate_limiting(self, client, db_session):
        """
        测试7：登录接口应有速率限制
        
        安全要求：登录接口应限制短时间内的请求次数，
        防止暴力破解攻击。
        
        CWE-307: Improper Restriction of Excessive Authentication Attempts
        """
        from app.services.auth_service import register_user
        
        # 创建测试用户
        register_user("rate_limit_test_user", "CorrectPassword123!", "user")
        db_session.session.commit()
        
        # 模拟暴力破解：连续发送10次错误密码请求
        failed_attempts = 0
        for i in range(10):
            response = client.post('/auth/login', json={
                'username': 'rate_limit_test_user',
                'password': f'WrongPassword{i}'
            })
            if response.status_code == 401:
                failed_attempts += 1
        
        # 再次尝试登录
        response = client.post('/auth/login', json={
            'username': 'rate_limit_test_user',
            'password': 'AnotherWrongPassword'
        })
        
        # 期望：应返回429 Too Many Requests，表示已被速率限制
        assert response.status_code == 429, \
            f"安全漏洞: 连续{failed_attempts}次失败登录后，接口仍返回 {response.status_code} 而不是 429，缺少速率限制保护"


class TestDataValidation:
    """数据验证测试类 - 用于发现业务数据验证缺陷"""
    
    def test_camera_ip_format_sql_injection(self, client, db_session):
        """
        测试8：摄像头IP地址应防止特殊字符注入
        
        安全要求：IP地址字段应只接受有效的IPv4格式，
        拒绝包含SQL注入或特殊字符的输入，并返回友好错误。
        
        CWE-89: SQL Injection / CWE-209: Error Message Information Leak
        """
        # 尝试在IP地址中注入SQL语句
        malicious_ip = "192.168.1.1'; DROP TABLE cameras;--"
        
        try:
            response = client.post('/camera/cameras', json={
                'name': 'Malicious Camera',
                'ip_address': malicious_ip,
                'port': 554,
                'url': 'rtsp://test',
                'resolution': '1920x1080',
                'frame_rate': 30,
                'encoding_format': 'H.264'
            })
            
            # 期望：应返回400验证错误，而不是500或其他错误
            assert response.status_code == 400, \
                f"安全漏洞: 包含特殊字符的IP地址应返回400验证错误，但返回了 {response.status_code}"
            
            # 验证响应消息表明是验证错误，而非泄露内部信息
            response_json = response.get_json()
            assert response_json is not None, "应返回JSON格式的错误信息"
        except Exception as e:
            # 如果抛出异常，说明错误处理不完善
            assert False, \
                f"错误处理缺陷: 非法IP地址导致未处理异常 - {type(e).__name__}: 系统应返回400验证错误而非暴露内部异常"
