import glob
import os
from PIL import Image
import shutil
import torch
import torch.nn as nn
from torchvision import transforms

class PageClassificator(nn.Module):
    def __init__(self):
        super(PageClassificator, self).__init__()
        # архитектура модели
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=5, padding=2)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5, padding=2)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(16384, 1024)
        self.relu3 = nn.ReLU()
        self.dropout = nn.Dropout(p=0.5)
        self.fc2 = nn.Linear(1024, 2)

    def forward(self, x):
        # прямой проход данных через слои
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.pool2(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu3(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return torch.sigmoid(x)

class PageValidator:
    def __init__(self, model_path, page_folder_path, uid=None, device='cpu') :
        self.model_path = model_path
        self.page_folder_path = page_folder_path
        self.uid = uid
        self.device = device
        self.waybills_folder_path = ''
        self.other_folder_path = ''

    def validate_images(self):
        self.create_folders()
        model = self.get_model()

        for image_path in glob.glob(f'{self.page_folder_path}/*.png', recursive=True):
            if self.uid is None or self.uid in str(image_path):
                self.recognize_image(image_path, model)

        return self.waybills_folder_path

    # создает папки для хранения изображений
    def create_folders(self):
        self.waybills_folder_path = f'{self.page_folder_path}/waybills'
        self.other_folder_path = f'{self.page_folder_path}/other'

        os.makedirs(f'{self.waybills_folder_path}', exist_ok=True)
        os.makedirs(f'{self.other_folder_path }', exist_ok=True)

    def get_model(self):
        model = torch.load(self.model_path,
                           map_location=torch.device(self.device),
                           weights_only=False,
                           )
        return model

    def recognize_image(self, image_path, model):
        img = Image.open(image_path)
        transform = self.get_transform()
        # преобразовываем изображение в тензор
        input_tensor = transform(img).unsqueeze(0)

        with torch.no_grad():  # Отключаем градиенты для ускоренной обработки
            input_tensor = input_tensor.to(torch.device(self.device))
            output = model(input_tensor)

        # получение класса с наибольшей вероятностью
        predicted_class = torch.argmax(output, dim=1)[0].item()
        # добавляем распознанные путевые листы в список
        self.move_to_folder(str(image_path), predicted_class)

    def move_to_folder(self, image_path, predicted_class):
        file_name = os.path.basename(image_path)

        if predicted_class == 1:
            new_image_path = f'{self.waybills_folder_path}/{file_name}'
        else:
            new_image_path = f'{self.other_folder_path}/{file_name}'

        shutil.move(image_path, new_image_path)

    @staticmethod
    def get_transform():
        transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Resize((64, 64)),
                                        transforms.Grayscale(num_output_channels=1)
                                        ])
        return transform




# if __name__ == '__main__':
#     import configparser
#
#     config = configparser.ConfigParser()
#     config.read(f'{ROOT_PATH}/settings.ini')
#
#     # пути каталогов для временных файлов хранятся в конфиге
#     PDF_FOLDER = config['ImagePath']['pdf']
#     ALL_PAGES_FOLDER = f'{ROOT_PATH}/{config['ImagePath']['all_pages']}'
#     VALID_PAGES_FOLDER = config['ImagePath']['valid_pages']
#     FIELDS_FOLDER = config['ImagePath']['fields']
#     TEXT_BOXES_FOLDER = config['ImagePath']['text_boxes']
#
#     # пути к ML моделям хранятся в конфиге
#     PAGE_VALIDATION_MODEL = f'{ROOT_PATH}/{config['ML_Models']['page_validation_model']}'
#     FIELDS_RECOGNITION_MODEL = config['ML_Models']['page_validation_model']
#     TEXT_BOXES_MODEL = config['ML_Models']['page_validation_model']
#
#     page_val = PageValidator(PAGE_VALIDATION_MODEL, ALL_PAGES_FOLDER)
#     page_val.get_waybills_list()
#     print(page_val.waybills_list)
