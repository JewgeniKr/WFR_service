import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app


@pytest.fixture
def app():
    """Фикстура для Flask приложения"""
    # Используем временную директорию для загрузок
    with tempfile.TemporaryDirectory() as tmpdir:
        flask_app.config['UPLOAD_FOLDER'] = tmpdir
        flask_app.config['TESTING'] = True
        yield flask_app

@pytest.fixture
def client(app):
    """Фикстура для тестового клиента"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Фикстура для CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def sample_pdf_file():
    """Создает временный файл для тестирования"""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'%PDF-1.4 fake pdf content')
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)