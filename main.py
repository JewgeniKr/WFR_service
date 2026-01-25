from app import app, db
from app.config import ProductionConfig
from sqlalchemy import inspect
from services.page_validation import PageClassificator

# Для разработки
app.config.from_object(ProductionConfig)

if __name__ == '__main__':
    with app.app_context():

        # Создаем инспектор для проверки существования таблиц
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        required_tables = ['images_types', 'images', 'ml_models_types', 'ml_models']

        # Проверяем существование таблиц
        missing_tables = [table for table in required_tables
                          if table not in existing_tables]

        if missing_tables:
            print(f"Создана таблица: {missing_tables}")
            db.create_all()
        else:
            print("Все таблицы уже существуют")

    app.run(debug=True, port=8080)
