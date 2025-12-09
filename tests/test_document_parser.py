import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Добавляем путь к корневой директории
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.document_parsing import DocumentParser

class TestDocumentParser:

    @pytest.fixture
    def temp_pdf_file(self):
        """Фикстура для временного PDF файла"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            # Создаем минимальный PDF файл
            f.write(
                b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\nxref\n0 2\n0000000000 65535 f\n0000000010 00000 n\ntrailer\n<<>>\nstartxref\n20\n%%EOF')
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def mock_config(self):
        """Мок конфигурации"""
        config_content = """
[ImagePath]
pdf = temp/pdf
all_pages = temp/all_pages
recognitions = temp/recognitions

[ML_Models]
page_validation_model = models/page_model.pth
fields_recognition_model = models/fields_model.pth
text_boxes_model = models/text_boxes_model.pth
text_recognition_model = models/text_recognition_model.pth

[WaybillFieldNumber]
1 = field1
2 = field2

[RecFieldsNumbers]
numbers = 1,2
"""
        return config_content

    def test_init(self, temp_pdf_file):
        """Тест инициализации"""
        parser = DocumentParser(temp_pdf_file)

        assert parser.input_file_path == temp_pdf_file
        assert parser.uid is not None
        assert len(parser.uid) == 36  # Длина UUID
        assert parser.valid_pages_folder_path == ''
        assert parser.file_name_recognition_folder_path == ''
        assert parser.file_name_validation_folder_path == ''
        assert parser.uid_validation_folder_path == ''

    @patch('services.document_parsing.configparser.ConfigParser')
    @patch('services.document_parsing.os.makedirs')
    def test_create_directories(self, mock_makedirs, mock_configparser, temp_pdf_file):
        """Тест создания директорий"""
        # Мокаем configparser
        mock_config = MagicMock()
        mock_configparser.return_value = mock_config
        mock_config.__getitem__.return_value = {'pdf': 'temp/pdf'}

        parser = DocumentParser(temp_pdf_file)

        # Вызываем метод
        parser.create_directories()

        # Проверяем что makedirs вызывался
        assert mock_makedirs.called

