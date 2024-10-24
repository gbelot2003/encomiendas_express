# app.services.conversation_history_service.py

from app.repositories.conversaion_repo import ConversacionRepo

class ConversationHistoryAction:
    def __init__(self, nombre_service=None, contacto_service=None):
        self.nombre_service = nombre_service
        self.contacto_service = contacto_service or ConversacionRepo

    def compilar_conversacion(self, user_id):
        # Recuperar el historial de conversaciones del usuario
        chat_history = ConversacionRepo.obtener_conversaciones_por_user_id(user_id)

        # Crear la lista de mensajes para enviar a OpenAI
        messages = []

        # Agregar el historial de conversaciones al prompt
        for conversacion in chat_history:
            messages.append({"role": "user", "content": conversacion.user_message})
            messages.append({"role": "assistant", "content": conversacion.bot_response})

        return messages