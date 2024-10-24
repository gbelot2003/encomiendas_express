# Archivo: config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Configuración común a todos los entornos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECRET_API_TOKEN = os.environ.get('SECRET_API_TOKEN') or 'default-api-token'  # Añade esta línea

class DevelopmentConfig(Config):
    # Configuración específica para el entorno de desarrollo
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance/dev.db')
    DEBUG = True

class TestingConfig(Config):
    # Configuración para el entorno de pruebas
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Base de datos en memoria
    TESTING = True
    DEBUG = False

class ProductionConfig(Config):
    # Configuración para el entorno de producción
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'instance/prod.db')
    DEBUG = False