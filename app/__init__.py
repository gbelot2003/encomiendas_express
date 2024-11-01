# Archivo: app/__init__.py

from flask import Flask
from flask_migrate import Migrate
from app.pdf_initializer import initialize_pdf_processing
from app.routes.main_router import configure_routes
from config import DevelopmentConfig, ProductionConfig, TestingConfig  # Importa la configuración adecuada
from app.extensions import db
from app.models import *

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)

    if config_class == DevelopmentConfig:
        app.config.from_object(DevelopmentConfig)
        initialize_pdf_processing()
    elif config_class == ProductionConfig:
        app.config.from_object(ProductionConfig)
        initialize_pdf_processing()
    else:
        app.config.from_object(TestingConfig)


    configure_routes(app)

    return app