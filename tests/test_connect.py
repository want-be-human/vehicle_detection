
import unittest
from app import create_app, socketio
from flask import url_for

class DetectionTestCase(unittest.TestCase):
    def setUp(self):
        """测试前初始化"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """测试后清理"""
        self.app_context.pop()

    def test_api_endpoint(self):
        """测试 API 端点"""
        response = self.client.get('/api/test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Backend server is running'})

    def test_websocket_connection(self):
        """测试 WebSocket 连接"""
        client = socketio.test_client(self.app)
        self.assertTrue(client.is_connected())

if __name__ == '__main__':
    unittest.main()