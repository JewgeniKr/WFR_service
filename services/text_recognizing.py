import os
from pathlib import Path
import configparser
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

class TextRecognition:
    def __init__(self, model_folder, image_folder, rec_fields_numbers):
        self.model_folder = model_folder
        self.image_folder = image_folder
        self.rec_fields_numbers = rec_fields_numbers

    def get_text(self):
        rec_text = {}

        # загрузка модели и процессора
        processor = TrOCRProcessor.from_pretrained(self.model_folder)
        model = VisionEncoderDecoderModel.from_pretrained(self.model_folder)

        folder = Path(self.image_folder).iterdir()
        for file in folder:
            file_name = os.path.basename(file)
            field_number = file_name[:file_name.find('_')]

            if field_number in self.rec_fields_numbers:
                field_name = self.get_field_name(file_name)
                image = Image.open(file).convert("RGB")

                # генерация предсказаний
                pixel_values = processor(images=image, return_tensors="pt").pixel_values
                generated_ids = model.generate(pixel_values)
                predicted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

                rec_text[field_name] = predicted_text

        return rec_text

    @staticmethod
    def get_field_name(file_name):
        first_symbol = file_name.find('_') + 1
        last_symbol = file_name.find('_conf')

        field_name = file_name[first_symbol:last_symbol]

        return field_name

if __name__ == '__main__':
    pass
