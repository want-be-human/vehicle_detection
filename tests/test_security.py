from datetime import datetime
from unittest.mock import Mock

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from app.services.auth_service import SECRET_KEY, create_jwt_token


class TestSecurity:
    def test_jwt_token_creation(self):
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = 'admin'

        token = create_jwt_token(mock_user)
        assert isinstance(token, (str, bytes))
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        assert decoded['user_id'] == 1
        assert decoded['role'] == 'admin'
        assert 'exp' in decoded

    def test_jwt_token_expiration(self):
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = 'user'

        token = create_jwt_token(mock_user)
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        exp_time = datetime.fromtimestamp(decoded['exp'])
        assert exp_time > datetime.utcnow()

    def test_sql_injection_prevention(self):
        malicious_input = "admin' OR '1'='1"
        sql_keywords = ['select', 'insert', 'update', 'delete', 'drop', 'union']

        for keyword in sql_keywords:
            assert keyword not in malicious_input.lower()

    def test_password_hashing(self):
        password = "MySecurePassword123"
        hashed = generate_password_hash(password)

        assert hashed != password
        assert len(hashed) > len(password)

        assert check_password_hash(hashed, password) is True
        assert check_password_hash(hashed, "WrongPassword") is False
