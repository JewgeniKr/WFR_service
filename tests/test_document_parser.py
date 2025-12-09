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

    @patch('services.document_parsing.fitz.open')
    def test_pdf_to_img(self, mock_fitz_open, temp_pdf_file):
        """Тест конвертации PDF в изображения"""
        # Мокаем fitz
        mock_page = MagicMock()
        mock_pixmap = MagicMock()
        mock_page.get_pixmap.return_value = mock_pixmap
        mock_pixmap.save = MagicMock()

        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = [mock_page, mock_page]  # Две страницы
        mock_fitz_open.return_value = mock_doc

        parser = DocumentParser(temp_pdf_file)
        parser.uid_validation_folder_path = '/tmp/test'

        # Вызываем метод
        parser.pdf_to_img()

        # Проверяем что save вызывался для каждой страницы
        assert mock_pixmap.save.call_count == 2

    @patch('services.document_parsing.page_validation.PageValidator')
    def test_validate_pages(self, mock_page_validator, temp_pdf_file):
        """Тест валидации страниц"""
        # Мокаем PageValidator
        mock_validator = MagicMock()
        mock_validator.validate_images.return_value = '/tmp/valid_pages'
        mock_page_validator.return_value = mock_validator

        parser = DocumentParser(temp_pdf_file)
        parser.uid_validation_folder_path = '/tmp/test'

        # Вызываем метод
        parser.validate_pages()

        # Проверяем
        mock_page_validator.assert_called_once()
        mock_validator.validate_images.assert_called_once()
        assert parser.valid_pages_folder_path == '/tmp/valid_pages'

    @patch('services.document_parsing.fields_finding.FieldFinder')
    def test_find_fields(self, mock_field_finder, temp_pdf_file):
        """Тест поиска полей"""
        # Мокаем FieldFinder
        mock_finder = MagicMock()
        mock_field_finder.return_value = mock_finder

        parser = DocumentParser(temp_pdf_file)
        parser.valid_pages_folder_path = '/tmp/valid_pages'
        parser.file_name_recognition_folder_path = '/tmp/recognition'

        # Вызываем метод
        parser.find_fields()

        # Проверяем
        mock_field_finder.assert_called_once()
        mock_finder.find_fields.assert_called_once()

    @patch('services.document_parsing.text_boxes_finding.TextBoxesFinder')
    @patch('services.document_parsing.Path')
    def test_find_text_boxes(self, mock_path, mock_text_boxes_finder, temp_pdf_file):
        """Тест поиска текстовых блоков"""
        # Мокаем Path и его итератор
        mock_folder = MagicMock()
        mock_folder.is_dir.return_value = True
        mock_folder.name = 'test_uid_folder'
        mock_folder.__str__.return_value = '/tmp/test'

        mock_path_obj = MagicMock()
        mock_path_obj.iterdir.return_value = [mock_folder]
        mock_path.return_value = mock_path_obj

        # Мокаем TextBoxesFinder
        mock_finder = MagicMock()
        mock_text_boxes_finder.return_value = mock_finder

        parser = DocumentParser(temp_pdf_file)
        parser.uid = 'test_uid'
        parser.file_name_recognition_folder_path = '/tmp/recognition'

        # Вызываем метод
        parser.find_text_boxes()

        # Проверяем
        mock_text_boxes_finder.assert_called_once()
        mock_finder.find_text_boxes.assert_called_once()

    @patch('services.document_parsing.text_recognizing.TextRecognition')
    @patch('services.document_parsing.Path')
    def test_recognize_text(self, mock_path, mock_text_recognition, temp_pdf_file):
        """Тест распознавания текста"""
        # Мокаем Path
        mock_folder = MagicMock()
        mock_folder.is_dir.return_value = True
        mock_folder.name = 'test_uid_folder'
        mock_folder.__str__.return_value = '/tmp/test'

        mock_path_obj = MagicMock()
        mock_path_obj.iterdir.return_value = [mock_folder]
        mock_path.return_value = mock_path_obj

        # Мокаем TextRecognition
        mock_rec = MagicMock()
        mock_rec.get_text.return_value = {'field1': 'value1', 'field2': 'value2'}
        mock_text_recognition.return_value = mock_rec

        parser = DocumentParser(temp_pdf_file)
        parser.uid = 'test_uid'
        parser.file_name_recognition_folder_path = '/tmp/recognition'

        # Вызываем метод
        result = parser.recognize_text()

        # Проверяем
        mock_text_recognition.assert_called_once()
        mock_rec.get_text.assert_called_once()
        assert 'test_uid_folder' in result
        assert result['test_uid_folder'] == {'field1': 'value1', 'field2': 'value2'}

    @patch('services.document_parsing.DocumentParser.create_directories')
    @patch('services.document_parsing.DocumentParser.pdf_to_img')
    @patch('services.document_parsing.DocumentParser.validate_pages')
    @patch('services.document_parsing.DocumentParser.find_fields')
    @patch('services.document_parsing.DocumentParser.find_text_boxes')
    @patch('services.document_parsing.DocumentParser.recognize_text')
    def test_get_text_values(self, mock_recognize_text, mock_find_text_boxes,
                             mock_find_fields, mock_validate_pages,
                             mock_pdf_to_img, mock_create_directories, temp_pdf_file):
        """Тест основного метода get_text_values"""
        # Настраиваем моки
        mock_recognize_text.return_value = {'result': 'test'}

        parser = DocumentParser(temp_pdf_file)

        # Вызываем основной метод
        result = parser.get_text_values()

        # Проверяем что все методы вызывались в правильном порядке
        mock_create_directories.assert_called_once()
        mock_pdf_to_img.assert_called_once()
        mock_validate_pages.assert_called_once()
        mock_find_fields.assert_called_once()
        mock_find_text_boxes.assert_called_once()
        mock_recognize_text.assert_called_once()

        # Проверяем результат
        assert result == {'result': 'test'}

    def test_uuid_generation(self, temp_pdf_file):
        """Тест на уникальный UUID"""
        parser1 = DocumentParser(temp_pdf_file)
        parser2 = DocumentParser(temp_pdf_file)

        assert parser1.uid != parser2.uid
        assert len(parser1.uid) == 36
        assert len(parser2.uid) == 36
