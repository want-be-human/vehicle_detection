"""
test_auth.py              # 用户认证测试
"""
import unittest
from app import create_app

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_login(self):
        response = self.client.post('/login', json={'username': 'admin', 'password': '123456'})
        self.assertEqual(response.status_code, 200)