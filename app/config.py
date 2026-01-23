import configparser
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]

config = configparser.ConfigParser()
config.read(f'{ROOT_PATH}/settings.ini')

# параметры подключения к БД хранятся в конфиге
USER = f'{config['Postgres']['user']}'
HOST = f'{config['Postgres']['host']}'
PASSWORD = f'{config['Postgres']['password']}'
DATABASE = f'{config['Postgres']['database']}'
PORT = f'{config['Postgres']['port']}'


class ProductionConfig(object):
    SECRET_KEY = 'do-or-do-not-there-is-no-try'
    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
