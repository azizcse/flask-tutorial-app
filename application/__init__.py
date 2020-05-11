from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tutorial.db')
app.config['JWT_SECRET_KEY'] = 'super-secret-tutorial-app-key'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

from application import route
