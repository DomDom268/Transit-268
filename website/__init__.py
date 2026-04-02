from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from os import path

from dotenv import load_dotenv

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
db = SQLAlchemy()

def create_app():
    # configure app
    app = Flask(__name__)
    os.makedirs(app.instance_path, exist_ok=True)

    load_dotenv()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    # initialize database
    db.init_app(app)

    #import tables from models.py
    from .models import Vehicle, Stops, Routes, Routes_Stops

    #register blueprints
    from .views import views
    app.register_blueprint(views, url_prefix = '/')
    
    #create database
    with app.app_context():
        db.create_all()

    return app


