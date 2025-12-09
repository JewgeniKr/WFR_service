import json
import io
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_root_route(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
