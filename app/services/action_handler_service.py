# archivo: app/services/action_handler_service.py

from app.actions.box_request_action import BoxRequestAction
from app.actions.verify_contact_action import VerifyContactAction
from app.repositories.chromadb_repo import ChromaDBRepo
from app.services.conversation_history_service import ConversationHistoryAction

class ActionHandleService:
    box_request_active = {}
    contact_verified = {}

    def __init__(self, user_id, prompt):
        self.user_id = user_id
        self.prompt = prompt
        self.messages = []
        self.box_request_action = BoxRequestAction(user_id)

        if self.user_id not in ActionHandleService.contact_verified:
            ActionHandleService.contact_verified[self.user_id] = False

    def handle_actions(self):
        # Verificar contacto al inicio
        if not ActionHandleService.contact_verified[self.user_id]:
            contact_action = VerifyContactAction()
            contact_verified_message = contact_action.verificar_contacto(self.user_id)

            # Marcar el contacto como verificado si corresponde
            if "Hola" in contact_verified_message:
                ActionHandleService.contact_verified[self.user_id] = True

            # Retornar el mensaje de bienvenida
            self.messages = [{"role": "assistant", "content": contact_verified_message}]
            return self.messages

        # Procesar la solicitud de BoxRequestAction si está activo
        if "solicitar caja" in self.prompt or ActionHandleService.box_request_active.get(self.user_id, False):
            ActionHandleService.box_request_active[self.user_id] = True
            box_request_message = self.box_request_action.handle_box_request(self.prompt)

            if self.box_request_action.state["step"] == "start":
                ActionHandleService.box_request_active[self.user_id] = False

            self.messages = [{"role": "assistant", "content": box_request_message}]
            return self.messages

        # Si no hay acción activa, proceder con una respuesta general
        general_response = self.default_unidos_express_response()
        self.messages.append({"role": "assistent", "content": general_response})
        return self.messages

    def default_unidos_express_response(self):
        return (
            "eres el asistente virtual de Unidos Express. y te comportas con respeto a cualquier usuario que te saludo. "
        )
