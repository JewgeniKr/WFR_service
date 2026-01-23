import cv2
import numpy as np
import os
from pathlib import Path
from ultralytics import YOLO
from services import db_actions

# параметры:
# папка с распознанными полями например (e649e488-008d-4d96-b8f8-08ff2eb58cbf_9/fields)
# путь к модели
class TextBoxesFinder:
    def __init__(self, fields_folder_path, model_path):
        self.recognitions_folder_path = Path(fields_folder_path).resolve().parents[0]
        self.fields_folder_path = fields_folder_path
        self.model = YOLO(model_path, task='detect')

    def find_text_boxes(self):
        text_boxes_folder_path = self.create_text_boxes_folder()
        self.create_text_boxes(text_boxes_folder_path)

    def create_text_boxes_folder(self):
        text_boxes_folder_path = f'{self.recognitions_folder_path}/text_boxes'
        os.makedirs(text_boxes_folder_path, exist_ok=True)

        return text_boxes_folder_path

    def create_text_boxes(self, text_boxes_folder_path):
        for image_path in Path(self.fields_folder_path).rglob('*'):
            image = cv2.imread(str(image_path))
            # results = self.model(image, imgsz=640, iou=0.4, conf=0.4)[0]
            results = self.model(image)[0]

            # Получаем оригинальное изображение и результаты детекции
            orig_image = results.orig_img # Создаем копию исходного изображения
            classes_names = results.names
            classes = results.boxes.cls.cpu().numpy()
            boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

            # Обработка каждого обнаруженного объекта
            for idx, (class_id, box) in enumerate(zip(classes, boxes)):
                class_name = classes_names[int(class_id)]

                # Вырезаем область вокруг объекта
                x1, y1, x2, y2 = box
                cropped_object = orig_image[y1:y2, x1:x2]

                # Генерируем уникальное имя файла
                filename = f"{os.path.basename(os.path.splitext(image_path)[0])}_{idx + 1}.jpg"
                save_path = os.path.join(text_boxes_folder_path, filename)

                # Сохраняем вырезанный объект
                cv2.imwrite(save_path, cropped_object)

                # Сохранение адреса изображения в БД
                db_actions.save_image(save_path, 5)

                print(f"Сохранено изображение класса '{class_name}' в {save_path}")
