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

def test_recognize_no_file(client):
    """Тест запроса без файла"""
    response = client.post('/recognize')
    data = json.loads(response.data)
    assert response.status_code == 400
    assert 'error' in data
    assert data['error'] == 'No file part'

def test_recognize_empty_filename(client):
    """Тест запроса с пустым именем файла"""
    data = {'uploaded_file': (io.BytesIO(b''), '')}
    response = client.post('/recognize', data=data)
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data['error'] == 'No selected file'

def test_recognize_invalid_file_type(client):
    """Тест загрузки неподдерживаемого типа файла"""
    data = {'uploaded_file': (io.BytesIO(b'test content'), 'test.txt')}
    response = client.post('/recognize', data=data)
    data = json.loads(response.data)
    assert response.status_code == 400
    assert 'Do not allowed file type' in data['error']
