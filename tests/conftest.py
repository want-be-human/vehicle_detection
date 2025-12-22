import pytest
from unittest.mock import patch

from app import create_app, db


@pytest.fixture
def app():
    """Create a Flask app with an in-memory SQLite database for tests."""
    try:
        with patch('app.config.scheduler_config.scheduler.start'):
            app = create_app()
    except ImportError as exc:
        pytest.skip(f"Required dependency missing: {exc}", allow_module_level=True)

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client bound to the shared test app."""
    return app.test_client()
