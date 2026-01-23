from collections import namedtuple
import cv2
import glob
import os
from ultralytics import YOLO
from services import db_actions

# структура для записи файла вырезанного класса на диск
WriteStructure = namedtuple('WriteStructure', ['confidence', 'image'])

# класс создает папку по имени файла (используется uid), в ней подпапку fields
# и размещает в папке fields обрезанные изображения найденных полей (классов)
class FieldFinder:
    def __init__(self, waybills_folder_path, model_path, recognitions_folder_path, fields_names):
        self.waybills_folder_path = waybills_folder_path
        self.model = YOLO(model_path, task='detect')
        self.recognitions_folder_path = recognitions_folder_path
        self.fields_names = fields_names
        self.best_confidence_classes = {}
        self.waybills_files_paths = []

    def find_fields(self):
        print(glob.glob(f'{self.waybills_folder_path}/*.png'))
        for waybill_img_path in glob.glob(f'{self.waybills_folder_path}/*.png'):
            # сохраняем все пути к файлам путевых листов в свойство класса
            # в дальнейшем потребуется выводить ссылку на файл в результирующем json
            self.waybills_files_paths.append(waybill_img_path)
            file_name_folder = self.create_file_name_folder(waybill_img_path)
            fields_folder = self.create_field_folder(file_name_folder)
            self.recognize_fields(waybill_img_path)
            self.save_files(fields_folder)

    # создает папку по имени файла
    def create_file_name_folder(self, waybill_img_path):
        # получаем имя файла без расширения
        file_name = os.path.splitext(os.path.basename(waybill_img_path))[0]
        # создаем папку по имени файла
        file_name_folder_path = os.path.join(self.recognitions_folder_path, file_name)
        os.makedirs(file_name_folder_path, exist_ok=True)

        return file_name_folder_path

    @staticmethod
    def create_field_folder(file_name_folder_path):
        field_folder_path = f'{file_name_folder_path}/fields'
        os.makedirs(field_folder_path, exist_ok=True)

        return field_folder_path

    def check_detection_count(self, classes):
        found_classes = [int(class_number) for class_number in classes]
        not_detected_fields = [num for num in self.fields_names.values() if int(num) not in found_classes]
        if len(not_detected_fields) > 0:
            print(f'Not found field classes: {len(not_detected_fields)}')
            for not_detected_field in not_detected_fields:
                class_name = self.model.names[int(not_detected_field)]
                print(self.fields_names[class_name], class_name)

    # сохраняет в словарь self.best_confidence_classes найденные классы с лучшей уверенностью модели
    def choise_best_conf(self, field_class, confidence, image):
        write_structure = WriteStructure(confidence, image)

        if field_class in self.best_confidence_classes:
            if confidence > self.best_confidence_classes[field_class].confidence:
                self.best_confidence_classes[field_class] = write_structure
        else:
            self.best_confidence_classes[field_class] = write_structure

    # распознает поля классов путевого листа и сохраняет данные в структуру для дальнейшей записи на диск
    def recognize_fields(self, waybill_img_path):
        self.best_confidence_classes = {}
        image = cv2.imread(waybill_img_path)

        # Предсказание объектов
        results = self.model(image, imgsz=640, iou=0.1, conf=0.1)

        # Получение bounding box'ов и классов
        boxes = results[0].boxes.xyxy  # Координаты bbox в формате [x1, y1, x2, y2]
        classes = results[0].boxes.cls  # Классы объектов
        confidences = results[0].boxes.conf  # Уверенность модели

        # проверка количества найденных классов
        self.check_detection_count(classes)

        # Перебираем все обнаруженные объекты
        for box, cls, conf in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = map(int, box)  # Преобразуем координаты в целые числа

            # Обрезаем объект из изображения
            object_img = image[y1:y2, x1:x2]
            # Получаем имя класса (если доступно)
            class_name = self.model.names[int(cls)]
            # добавляем в словарь для записи класс наилучшей уверенностью модели
            self.choise_best_conf(class_name, float(conf), object_img)

    def save_files(self, fields_folder):
        for class_name, write_structure in self.best_confidence_classes.items():

            # Сохраняем вырезанное изображение
            class_field_number = self.fields_names[class_name]
            output_path = f"{fields_folder}/{class_field_number}_{class_name}_conf_{write_structure.confidence:.2f}.jpg"
            cv2.imwrite(output_path, write_structure.image)

            # Сохранение адреса изображения в БД
            db_actions.save_image(output_path, 4)

        print(f"Сохранено {len(self.best_confidence_classes)} объектов в папку {fields_folder}")
