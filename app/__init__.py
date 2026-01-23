from flask import Flask
import os
from app.config import ProductionConfig
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basedir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.config.from_object(ProductionConfig)
db = SQLAlchemy(app)

from app import routes, db_models
