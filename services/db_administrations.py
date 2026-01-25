from app import config
import psycopg2

def create_db():
    try:
        # Создаем подключение и курсор
        conn = psycopg2.connect(
                dbname='postgres',
                user=config.USER,
                password=config.PASSWORD,
                host=config.HOST,
                port=config.PORT
        )
        cursor = conn.cursor()
        conn.autocommit = True

        # Проверяем, существует ли база данных
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config.DATABASE}'")

        if cursor.fetchone():
            print(f"База данных '{config.DATABASE}' уже существует")
        else:
            # Создаем базу данных
            cursor.execute(f"CREATE DATABASE {config.DATABASE}")
            print(f"База данных '{config.DATABASE}' успешно создана")

        cursor.close()
        conn.close()

    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
