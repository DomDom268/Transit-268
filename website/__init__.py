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

    #Only takes my local env variable if railway env not available
    if os.getenv("RAILWWAY_ENVIRONMENT") is None:
        load_dotenv()

    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logging.error("DATABASE_URL environment variable not set.")
        raise ValueError("DATABASE_URL environment variable not set.")

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"
        
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

    # initialize database
    db.init_app(app)

    #import tables from models.py
    from .models import Vehicle, Stops, Routes, Routes_Stops
    #register blueprints
    from .views import views
    app.register_blueprint(views, url_prefix = '/')
    
    if os.getenv("RAILWAY_ENVIRONMENT") is None: 
        logging.info("Running in local environment.")
        with app.app_context():
            db.create_all()

    return app


