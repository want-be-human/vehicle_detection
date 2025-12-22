import os

from app.config.config import Config
from app.config.scheduler_config import scheduler_config


def test_database_config(monkeypatch):
    config = Config()

    assert config.SQLALCHEMY_DATABASE_URI.startswith("mysql")
    assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False

    monkeypatch.setenv('SQLALCHEMY_ECHO', 'true')
    refreshed = Config()
    assert refreshed.SQLALCHEMY_ECHO is True


def test_path_config():
    config = Config()

    assert os.path.isabs(config.BASE_DIR)
    assert os.path.exists(config.BASE_DIR)
    assert os.path.exists(config.MODEL_DIR)
    assert os.path.exists(config.CONFIG_DIR)


def test_scheduler_config():
    assert 'executors' in scheduler_config
    assert 'job_defaults' in scheduler_config
    assert scheduler_config['job_defaults']['max_instances'] == 3
