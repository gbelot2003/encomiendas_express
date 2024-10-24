# Archivo: app/__init__.py

from flask import Flask
from flask_migrate import Migrate
from app.routes.main_router import configure_routes
from config import DevelopmentConfig  # Importa la configuración adecuada
from app.extensions import db
from app.models import *

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)

    configure_routes(app)

    return app