# archivo: app/services/action_handler_service.py

from app.actions.box_request_action import BoxRequestAction
from app.actions.distance_calculation_action import DistanceCalculationAction
from app.actions.name_action import NameAction
from app.actions.verify_contact_action import VerifyContactAction
from app.repositories.chromadb_repo import ChromaDBRepo
from app.services.conversation_history_service import ConversationHistoryAction

class ActionHandleService:
    def __init__(self, user_id, prompt):
        self.user_id = user_id
        self.prompt = prompt
        self.messages = []
        self.box_request_action = BoxRequestAction(user_id)  # Instancia de BoxRequestAction

    def handle_actions(self):
        # Bloqueo del flujo para BoxRequestAction
        if "solicitar caja" in self.prompt or self.box_request_action.state["step"] != "start":
            print("BoxRequestAction is active")  # Depuración para confirmar el flujo activo
            box_request_message = self.box_request_action.handle_box_request(self.prompt)
            print(f"BoxRequestAction response: {box_request_message}")  # Depuración adicional
            
            # Asignamos la respuesta de BoxRequestAction a self.messages y retornamos exclusivamente
            self.messages = [{"role": "assistant", "content": box_request_message}]
            return self.messages  # Retornar exclusivamente la respuesta de BoxRequestAction

        # Verificar si el usuario tiene un número de teléfono en la base de datos
        contacto = VerifyContactAction().verificar_contacto(self.user_id)

        # Buscar fragmentos relevantes en ChromaDB
        chromadb_repo = ChromaDBRepo()
        relevant_chunks = chromadb_repo.buscar_fragmentos_relevantes(self.prompt)
        if relevant_chunks:
            self.messages.append(relevant_chunks)

        # Buscar historial de conversación
        conversation_history_action = ConversationHistoryAction()
        chat_history_messages = conversation_history_action.compilar_conversacion(self.user_id)
        self.messages.extend(chat_history_messages)

        # Procesar el nombre del contacto
        name_action = NameAction(contacto, self.prompt)
        name_message = name_action.process_name()
        if name_message:
            self.messages.append(name_message)
        
        # Manejar la solicitud de cálculo de distancia
        if "distancia a" in self.prompt:
            destination_address = self.prompt.split("distancia a")[-1].strip()
            distance_action = DistanceCalculationAction(destination_address)
            distance_message = distance_action.handle()
            self.messages.append({"role": "assistant", "content": distance_message})
            return self.messages

        return self.messages
