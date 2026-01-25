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


# заполнение данными таблицы images_types
def init_images_types():

    sql_commands = [
        """
        INSERT INTO images_types (name) 
        VALUES ('PDF')
        ON CONFLICT (name) DO NOTHING;
        """,
        """
        INSERT INTO images_types (name) 
        VALUES ('Главная страница путевого листа')
        ON CONFLICT (name) DO NOTHING;
        """,
        """
        INSERT INTO images_types (name) 
        VALUES ('Прочая страница путевого листа')
        ON CONFLICT (name) DO NOTHING;
        """,
        """
        INSERT INTO images_types (name) 
        VALUES ('Поле путевого листа')
        ON CONFLICT (name) DO NOTHING;
        """,
        """
        INSERT INTO images_types (name) 
        VALUES ('Текстовый бокс')
        ON CONFLICT (name) DO NOTHING;
        """
    ]

    try:
        conn = psycopg2.connect(
            dbname=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            host=config.HOST,
            port=config.PORT,
        )
        cursor = conn.cursor()

        for sql in sql_commands:
            cursor.execute(sql)

        conn.commit()
        print("Таблица images_types успешно инициализирована")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка: {e}")