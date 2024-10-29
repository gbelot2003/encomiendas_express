# app/services/action_handler_service.py
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
            # Extraer la dirección de destino del prompt
            destination_address = self.prompt.split("distancia a")[-1].strip()
            distance_action = DistanceCalculationAction(destination_address)
            distance_message = distance_action.handle()
            
            print(distance_message)
            # Asegurarnos de que el mensaje de distancia sea el último en agregarse
            self.messages.append({"role": "assistant", "content": distance_message})
            return [{"role": "assistant", "content": distance_message}]  # Devolvemos la respuesta de distancia como única salida
        
        # Manejar la solicitud de caja
        elif "solicitar caja" in self.prompt or self.box_request_action.state["step"] != "start":
            box_request_message = self.box_request_action.handle_box_request(self.prompt)
            self.messages.append({"role": "assistant", "content": box_request_message})
            return [{"role": "assistant", "content": box_request_message}]

        return self.messages
