"""
Module containing the configuration for the application.
"""
import os

from dotenv import load_dotenv

load_dotenv()
# App Flask Config
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    USER_ENABLE_EMAIL = False
    UPLOAD_FOLDER = "static/files"
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    FLASK_APP= os.environ.get('FLASK_APP')

class DevelopmentConfig(Config):
    DEBUG = os.environ.get('DEBUG')
    FLASK_ENV= os.environ.get('FLASK_ENV_DEV')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    print('DevelopmentConfig'.center(80, '-'))


class TestingConfig(Config):
    TESTING = os.environ.get('TESTING')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'


class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = os.environ.get('DEBUG_PROD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    FLASK_RUN_PORT = os.environ.get('FLASK_RUN_PORT')
    FLASK_RUN_HOST = os.environ.get('FLASK_RUN_HOST')
    print('ProductionConfig'.center(80, '-'))

config = {
    "development":DevelopmentConfig,
    "testing":TestingConfig,
    "production":ProductionConfig,
    "default":DevelopmentConfig
}

# Connection PostgreSQL

keepalive_kwargs = {
    "keepalives": 1,
    "keepalives_idle": 60,
    "keepalives_interval": 10,
    "keepalives_count": 5
}