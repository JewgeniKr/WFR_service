import os
from pathlib import Path
import random
import shutil

'''создает датасет для TROcR на основании текстбоксов'''
class DatasetCreator:
    def __init__(self,
                 source_folder = 'C:/_waybill_recognition/prod_1/temp/recognitions',
                 target_folder = 'C:/_waybill_recognition/prod_1/dataset_by_textboxes'
                 ):
        self.source_folder = source_folder
        self.target_folder = target_folder
        self.files_paths = []

    def create(self):
        os.makedirs(self.target_folder, exist_ok=True)
        self.get_files_paths()
        self.copy_files_to_new_dataset_folder()

    def get_files_paths(self):
        source_folder_path = Path(self.source_folder)
        text_box_folders = [tb_folder for tb_folder in source_folder_path.rglob('text_boxes')]

        for text_box_folder in text_box_folders:
            path = Path(text_box_folder)
            [self.files_paths.append(elem) for elem in path.rglob('*') if elem.is_file()]

    def copy_files_to_new_dataset_folder(self):
        number = 1
        for file_path in self.files_paths:
            file_name_with_ext = os.path.basename(file_path)
            file_name, ext = os.path.splitext(file_name_with_ext)

            new_file_name = f'{file_name}_{number}{ext}'
            destination_file = f'{self.target_folder}/{new_file_name}'

            # Копируем файл в другую папку с новым именем
            shutil.copyfile(file_path, destination_file)
            number += 1

'''Равномерно распределяет файлы исходя из их классов'''
class DatasetDistributor:
    def __init__(self, dataset_folder, destination_folder):
        self.dataset_folder = dataset_folder
        self.destination_folder = destination_folder
        self.files = os.listdir(self.dataset_folder)
        self.numbers_of_classes = {0: [],
                                   1: [],
                                   2: [],
                                   3: [],
                                   4: [],
                                   5: [],
                                   6: [],
                                   7: [],
                                   9: [],
                                   10: [],
                                   11: {1: [],
                                        2: [],
                                        3: [],
                                        4: [],
                                        5: [],
                                        6: [],
                                        },
                                   12: [],
                                   13: [],
                                   14: {1: [],
                                        2: [],
                                        3: [],
                                        },
                                   }
        self.part = []

    def get_distribution(self):
        os.makedirs(self.destination_folder, exist_ok=True)
        self.get_numbers_of_classes()

        for k, v in self.numbers_of_classes.items():
            if k in (11, 14):
                for key, value in v.items():
                    part_size = len(value) // 10
                    random_part = random.sample(value, k=part_size)
                    [self.move_file_to_folder(file) for file in random_part]
            else:
                part_size = len(v) // 10
                random_part = random.sample(v, k=part_size)
                [self.move_file_to_folder(file) for file in random_part]

    def get_numbers_of_classes(self):
        for file in self.files:
            file_basename = os.path.basename(file)
            class_number = int(file_basename.split('_')[0])

            if class_number in (11, 14):
                sub_class_number = int(file_basename.split('_')[-2])
                if sub_class_number <= 6:
                    self.numbers_of_classes[class_number][sub_class_number].append(file)
            else:
                self.numbers_of_classes[class_number].append(file)

    def move_file_to_folder(self, file_name):
        file_path = f'{self.dataset_folder}/{file_name}'
        destination_file = f'{self.destination_folder}/{file_name}'

        shutil.move(file_path, destination_file)
        print(f'Файл "{file_path}" успешно перемещен в "{destination_file}"')


def create_text_annotation(source_path):
    files = os.listdir(source_path)

    with open('test.tsv', 'w', encoding='utf-8') as annotation_file:
        for file in files:
            annotation_file.write(f'{file}\n')

if __name__ == '__main__':
    recognitions_folder = 'C:/_waybill_recognition/prod_1/temp/recognitions'
    target = 'C:/_waybill_recognition/prod_1/dataset_by_textboxes'
    move_folder = 'C:/_waybill_recognition/prod_1/split_dataset'

    test_folder_path = 'C:/_waybill_recognition/prod_1/split_dataset_prod/test'
    train_folder_path = 'C:/_waybill_recognition/prod_1/dataset_by_textboxes'

    # dataset_creator = DatasetCreator(recognitions_folder, target)
    # dataset_creator.create()

    # dataset_dist = DatasetDistributor(target, test_folder_path)
    # dataset_dist.get_distribution()

    create_text_annotation(test_folder_path)
