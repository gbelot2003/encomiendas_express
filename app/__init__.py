# Archivo: app/__init__.py

from flask import Flask
from flask_migrate import Migrate
from app.actions.chromadb_action import ChromaDBAction
from app.actions.embedding_processing_action import EmbeddingProcessingAction
from app.actions.pdf_processing_action import PDFProcessingService
from app.routes.main_router import configure_routes
from config import DevelopmentConfig  # Importa la configuración adecuada
from app.extensions import db
from app.models import *

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)

    # Lista de rutas de archivos PDF
    pdf_paths = [
        "files/encomiendas.pdf",
        # Agrega más rutas de archivos PDF aquí
    ]

    # Procesar cada PDF al iniciar la aplicación
    for pdf_path in pdf_paths:
        try:
            text = PDFProcessingService().extract_text_from_pdf(pdf_path)
            chunks = PDFProcessingService().split_text_into_chunks(text)
            chunks_with_embeddings = [(chunk, EmbeddingProcessingAction().get_embedding_for_chunk(chunk)) for chunk in chunks]
            ChromaDBAction().store_chunks_in_chromadb(chunks_with_embeddings, pdf_path)
        except Exception as e:
            print(f"Error procesando el PDF {pdf_path}: {e}")


    configure_routes(app)

    return app