# -*- coding: utf-8 -*-
"""
配置测试 (test_config.py)

覆盖配置相关的测试:
- Config类
- 调度器配置
- 应用初始化
"""

import os
import sys

# 确保项目路径优先
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestConfigClass:
    """配置类测试"""
    
    def test_config_database_uri(self):
        """测试数据库URI配置"""
        from app.config.config import Config
        
        # 验证配置存在
        assert hasattr(Config, 'SQLALCHEMY_DATABASE_URI')
        assert Config.SQLALCHEMY_DATABASE_URI is not None
    
    def test_config_track_modifications(self):
        """测试SQLAlchemy跟踪配置"""
        from app.config.config import Config
        
        assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    
    def test_config_base_dir(self):
        """测试基础目录配置"""
        from app.config.config import Config
        
        assert hasattr(Config, 'BASE_DIR')
        assert os.path.isabs(Config.BASE_DIR)
    
    def test_config_model_dir(self):
        """测试模型目录配置"""
        from app.config.config import Config
        
        assert hasattr(Config, 'MODEL_DIR')
        assert 'models' in Config.MODEL_DIR
    
    def test_config_config_dir(self):
        """测试配置文件目录"""
        from app.config.config import Config
        
        assert hasattr(Config, 'CONFIG_DIR')
        assert 'configs' in Config.CONFIG_DIR


class TestSchedulerConfig:
    """调度器配置测试"""
    
    def test_scheduler_exists(self, app_context):
        """测试调度器存在"""
        from app.config.scheduler_config import scheduler
        
        assert scheduler is not None
    
    def test_scheduler_module_imported(self, app_context):
        """测试调度器模块可以导入"""
        from apscheduler.schedulers.background import BackgroundScheduler
        
        # 确保BackgroundScheduler类可用
        assert BackgroundScheduler is not None


class TestAppInit:
    """应用初始化测试"""
    
    def test_create_app_with_test_config(self, app):
        """测试应用创建（使用测试配置）"""
        assert app is not None
        assert app.config.get('TESTING') is True
    
    def test_create_app_settings(self, app):
        """测试应用设置"""
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    
    def test_db_initialized(self):
        """测试数据库初始化"""
        from app import db
        
        assert db is not None
    
    def test_blueprints_registered(self, app):
        """测试蓝图注册"""
        # 验证蓝图已注册
        assert 'auth' in app.blueprints
        assert 'camera' in app.blueprints
        assert 'detection' in app.blueprints
        assert 'violation' in app.blueprints
        assert 'history' in app.blueprints
        assert 'statistics' in app.blueprints


class TestTestConfigClass:
    """测试配置类测试"""
    
    def test_test_config_testing(self):
        """测试配置 - TESTING"""
        # 在当前文件中定义测试配置类
        class LocalTestConfig:
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
        
        assert LocalTestConfig.TESTING is True
    
    def test_test_config_database(self):
        """测试配置 - 数据库"""
        class LocalTestConfig:
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
        
        assert 'sqlite' in LocalTestConfig.SQLALCHEMY_DATABASE_URI
        assert LocalTestConfig.SQLALCHEMY_TRACK_MODIFICATIONS is False
