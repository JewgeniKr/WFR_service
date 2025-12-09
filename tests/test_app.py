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

@patch('app.other_destination.allowed_file')
@patch('app.document_parsing.DocumentParser')
def test_recognize_success(MockDocumentParser, mock_allowed_file, client):
    """Тест успешной обработки файла"""
    # Мокаем разрешение файла
    mock_allowed_file.return_value = True

    # Мокаем DocumentParser
    mock_parser = MagicMock()
    mock_parser.get_text_values.return_value = {'text': 'parsed content'}
    MockDocumentParser.return_value = mock_parser

    # Отправляем файл
    data = {'uploaded_file': (io.BytesIO(b'PDF content'), 'test.pdf')}
    response = client.post('/recognize', data=data)

    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'text' in data
    assert data['text'] == 'parsed content'

    # Проверяем, что парсер был вызван
    MockDocumentParser.assert_called_once()
    mock_parser.get_text_values.assert_called_once()

@patch('app.other_destination.allowed_file')
def test_file_saving(mock_allowed_file, app, client):
    """Тест сохранения файла на диск"""
    mock_allowed_file.return_value = True

    # Мокаем document_parsing чтобы не зависеть от реальной логики
    with patch('app.document_parsing.DocumentParser') as MockParser:
        mock_parser = MagicMock()
        mock_parser.get_text_values.return_value = {}
        MockParser.return_value = mock_parser

        # Создаем тестовый файл
        file_content = b'Test PDF content'
        data = {'uploaded_file': (io.BytesIO(file_content), 'document.pdf')}

        response = client.post('/recognize', data=data)

        assert response.status_code == 200

        # Проверяем, что файл был сохранен
        import os
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'document.pdf')
        assert os.path.exists(file_path)

        # Проверяем содержимое файла
        with open(file_path, 'rb') as f:
            assert f.read() == file_content

def test_upload_folder_creation(app):
    """Тест создания папки для загрузок"""
    import os
    assert os.path.exists(app.config['UPLOAD_FOLDER'])
    assert os.path.isdir(app.config['UPLOAD_FOLDER'])