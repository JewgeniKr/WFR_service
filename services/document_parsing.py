import configparser
import fitz
import os
from pathlib import Path
from services import page_validation, fields_finding, text_boxes_finding, text_recognizing

import uuid
# from fields_finding import FieldFinder
# from text_boxes_finding import TextBoxesFinder
# from text_recognizing import TextRecognition

ROOT_PATH = Path(__file__).resolve().parents[1]

config = configparser.ConfigParser()
config.read(f'{ROOT_PATH}/settings.ini')

# пути каталогов для временных файлов хранятся в конфиге
PDF_FOLDER = f'{ROOT_PATH}/{config['ImagePath']['pdf']}'
ALL_PAGES_FOLDER = f'{ROOT_PATH}/{config['ImagePath']['all_pages']}'
RECOGNITIONS_FOLDER = f'{ROOT_PATH}/{config['ImagePath']['recognitions']}'

# пути к ML моделям хранятся в конфиге
PAGE_VALIDATION_MODEL = f'{ROOT_PATH}/{config['ML_Models']['page_validation_model']}'
FIELDS_RECOGNITION_MODEL = f'{ROOT_PATH}/{config['ML_Models']['fields_recognition_model']}'
TEXT_BOXES_MODEL = f'{ROOT_PATH}/{config['ML_Models']['text_boxes_model']}'
TEXT_RECOGNITION_MODEL = f'{ROOT_PATH}/{config['ML_Models']['text_recognition_model']}'

waybill_field_number_section = config['WaybillFieldNumber']
WAYBILL_FIELDS_NAMES = {i: waybill_field_number_section[i] for i in waybill_field_number_section}

REC_FIELDS_NUMBERS = config['RecFieldsNumbers']['numbers']

class DocumentParser:
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.uid = str(uuid.uuid4())
        self.valid_pages_folder_path = ''
        self.file_name_recognition_folder_path = ''
        self.file_name_validation_folder_path = ''
        self.uid_validation_folder_path = ''

    def get_text_values(self):

        # шаг 1: создаем структуру каталогов временных файлов при ее отсутствии
        self.create_directories()

        # шаг 2: Преобразуем PDF в изображения
        self.pdf_to_img()

        # шаг 3: Выбираем только страницы с полезной информацией
        self.validate_pages()

        # шаг 4: Выделяем полезные участки документа
        self.find_fields()

        # шаг 5: С большей детализацией выбираем уточненные текстовые блоки
        self.find_text_boxes()

        # шаг 6: Распознаем текст
        result = self.recognize_text()

        return result

    def create_directories(self):
        # получаем имя файла без расширения
        file_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
        # создаем папки по имени файла
        self.file_name_recognition_folder_path = os.path.join(RECOGNITIONS_FOLDER, file_name)
        self.file_name_validation_folder_path = os.path.join(ALL_PAGES_FOLDER, file_name)
        self.uid_validation_folder_path = os.path.join(self.file_name_validation_folder_path, self.uid)

        folders = (PDF_FOLDER,
                   ALL_PAGES_FOLDER,
                   RECOGNITIONS_FOLDER,
                   self.file_name_recognition_folder_path,
                   self.file_name_validation_folder_path,
                   self.uid_validation_folder_path
                   )

        [os.makedirs(folder, exist_ok=True) for folder in folders]

    def pdf_to_img(self):
        images = []
        with fitz.open(self.input_file_path) as pdf_doc:
            for i, page in enumerate(pdf_doc):
                pixmap = page.get_pixmap()
                output_file = f'{self.uid_validation_folder_path}/{self.uid}_{i + 1}.png'
                pixmap.save(output_file)
                images.append(output_file)

    def validate_pages(self):
        page_validator = page_validation.PageValidator(PAGE_VALIDATION_MODEL, self.uid_validation_folder_path, self.uid)
        self.valid_pages_folder_path = page_validator.validate_images()

    def find_fields(self):
        field_finder = fields_finding.FieldFinder(self.valid_pages_folder_path, FIELDS_RECOGNITION_MODEL, self.file_name_recognition_folder_path, WAYBILL_FIELDS_NAMES)
        field_finder.find_fields()

    def find_text_boxes(self):
        folders = Path(self.file_name_recognition_folder_path).iterdir()

        for folder_path in folders:
            if folder_path.is_dir() and self.uid in folder_path.name:
                text_boxes_finder = text_boxes_finding.TextBoxesFinder(f'{folder_path}/fields', TEXT_BOXES_MODEL)
                text_boxes_finder.find_text_boxes()

    def recognize_text(self):
        result = {}

        folders = Path(self.file_name_recognition_folder_path).iterdir()
        for folder_path in folders:
            if folder_path.is_dir() and self.uid in folder_path.name:
                text_box_folder = f'{folder_path}/text_boxes'
                text_rec = text_recognizing.TextRecognition(TEXT_RECOGNITION_MODEL, text_box_folder, REC_FIELDS_NUMBERS)
                text_dict = text_rec.get_text()
                result[folder_path.name] = text_dict

        return result

if __name__ == '__main__':
    # doc = DocumentParser(f'{ROOT_PATH}/temp/pdf/180.pdf')
    # doc.create_directories()
    # doc.pdf_to_img()
    #
    # page_val = PageValidator(PAGE_VALIDATION_MODEL, ALL_PAGES_FOLDER)
    # page_val.get_waybills_list()
    # wb_list = page_val.waybills_list

    # print(wb_list)
    #
    # ff = FieldFinder(page_val.waybills_list, FIELDS_RECOGNITION_MODEL, RECOGNITIONS_FOLDER, WAYBILL_FIELDS_NAMES)
    # ff.find_fields()

    # test single document
    new_parser = DocumentParser(f'{ROOT_PATH}/temp/pdf/172.pdf')
    res = new_parser.get_text_values()
    print(res)

    # # test folder with documents
    # for doc in Path(f'{ROOT_PATH}/temp/pdf').rglob('*'):
    #     parser = DocumentParser(doc)
    #     parser.get_text_values()
