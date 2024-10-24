# archivo: app/repositories/conversaion_repo.py

from app.extensions import db
from app.models.conversation_model import Conversation

class ConversacionRepo:
    @staticmethod
    def crear_conversacion(user_message, bot_response, user_id):
        nueva_conversacion = Conversation(user_message=user_message, bot_response=bot_response, user_id=user_id)
        db.session.add(nueva_conversacion)
        db.session.commit()
        return nueva_conversacion

    @staticmethod
    def obtener_conversaciones_por_user_id(user_id):
        return Conversation.query.filter_by(user_id=user_id).all()

    @staticmethod
    def obtener_todas_conversaciones():
        return Conversation.query.all()

    @staticmethod
    def eliminar_conversacion(conversacion_id):
        conversacion = Conversation.query.filter_by(id=conversacion_id).first()
        if conversacion:
            db.session.delete(conversacion)
            db.session.commit()
        return conversacion