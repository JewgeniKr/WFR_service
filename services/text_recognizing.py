import os
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np


class TextRecognition:
    def __init__(self, model, image_folder, rec_fields_numbers, waybill_file_path):
        self.model = model
        self.image_folder = image_folder
        self.rec_fields_numbers = rec_fields_numbers
        self.waybill_file_path = waybill_file_path

    def get_text(self):
        rec_text = {}

        yolo_model = YOLO(self.model)
        folder = Path(self.image_folder).iterdir()

        rec_text['image_url'] = self.waybill_file_path

        for file in folder:
            file_name = os.path.basename(file)
            field_number = file_name[:file_name.find('_')]

            if field_number in self.rec_fields_numbers:
                field_name = self.get_field_name(file_name)
                image = cv2.imread(str(file))

                # Предсказание
                results = yolo_model(image, imgsz=640, iou=0.4, conf=0.5, verbose=True)[0]

                classes = results.boxes.cls.cpu().numpy()
                boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

                classes_names = results.names
                result_string = ''

                if len(boxes) > 0:
                    # Сортируем индексы по левой границе
                    sorted_indices = boxes[:, 0].argsort()

                    for indx in sorted_indices:
                        result_string += classes_names[int(classes[indx])]

                rec_text[field_name] = result_string
                rec_text[f'{field_name}_image'] = self.get_img_url(str(file))

        return rec_text

    @staticmethod
    def get_img_url(file_path):
        uni_file_path = file_path.replace('\\', '/')
        url_safe = uni_file_path.split('temp')[1]

        image_url = f'/field_name{url_safe}'

        return image_url

    @staticmethod
    def get_field_name(file_name):
        first_symbol = file_name.find('_') + 1
        last_symbol = file_name.find('_conf')

        field_name = file_name[first_symbol:last_symbol]

        return field_name


if __name__ == '__main__':
    pass
