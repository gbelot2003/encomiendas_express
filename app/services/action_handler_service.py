# archivo: app/services/action_handler_service.py

from datetime import datetime, timedelta
from app.actions.box_request_action import BoxRequestAction
from app.actions.distance_calculation_action import DistanceCalculationAction
from app.actions.name_action import NameAction
from app.actions.verify_contact_action import VerifyContactAction
from app.repositories.chromadb_repo import ChromaDBRepo
from app.services.conversation_history_service import ConversationHistoryAction

class ActionHandleService:
    # Tiempo de expiración para el flujo de BoxRequestAction
    EXPIRATION_TIME = timedelta(minutes=10)
    # Variable de clase para rastrear el estado de BoxRequestAction con timestamps
    box_request_active = {}

    def __init__(self, user_id, prompt):
        self.user_id = user_id
        self.prompt = prompt
        self.messages = []
        self.box_request_action = BoxRequestAction(user_id)  # Instancia de BoxRequestAction

        # Inicializar el estado de la variable de bloqueo por usuario con None si es la primera vez
        if self.user_id not in ActionHandleService.box_request_active:
            ActionHandleService.box_request_active[self.user_id] = None

    def handle_actions(self):
        # Verificar si el flujo está activo y ha expirado
        last_active = ActionHandleService.box_request_active.get(self.user_id)
        if last_active and datetime.now() - last_active > ActionHandleService.EXPIRATION_TIME:
            # Resetear el estado si ha expirado
            ActionHandleService.box_request_active[self.user_id] = None

        # Activar o continuar el flujo de BoxRequestAction si no ha expirado
        if "c" in self.prompt or ActionHandleService.box_request_active.get(self.user_id):
            # Marcar el inicio del flujo si es la primera vez
            if not ActionHandleService.box_request_active[self.user_id]:
                ActionHandleService.box_request_active[self.user_id] = datetime.now()

            # Procesar la solicitud de caja
            box_request_message = self.box_request_action.handle_box_request(self.prompt)

            # Desactivar el flujo si el estado de BoxRequestAction vuelve a "start"
            if self.box_request_action.state["step"] == "start":
                ActionHandleService.box_request_active[self.user_id] = None

            # Retornar solo el mensaje de BoxRequestAction
            self.messages = [{"role": "assistant", "content": box_request_message}]
            return self.messages

        # Procesos habituales si BoxRequestAction no está activo
        contacto = VerifyContactAction().verificar_contacto(self.user_id)
        
        chromadb_repo = ChromaDBRepo()
        relevant_chunks = chromadb_repo.buscar_fragmentos_relevantes(self.prompt)
        if relevant_chunks:
            self.messages.append(relevant_chunks)

        conversation_history_action = ConversationHistoryAction()
        chat_history_messages = conversation_history_action.compilar_conversacion(self.user_id)
        self.messages.extend(chat_history_messages)

        name_action = NameAction(contacto, self.prompt)
        name_message = name_action.process_name()
        if name_message:
            self.messages.append(name_message)

        return self.messages
