from app.db_models import Image
from app import db
import os

def save_image(img_path, img_type_code):
    clear_img_address = img_path.replace('\\', '/')
    # создаем экземпляр изображения
    new_image = Image(name=os.path.basename(img_path),
                      image_type_id=img_type_code,
                      address=clear_img_address)

    try:
        # Добавляем в сессию и сохраняем
        db.session.add(new_image)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(e)
