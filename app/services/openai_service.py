# archivo: app/services/openai_service.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from app.repositories.conversaion_repo import ConversacionRepo
from app.services.action_handler_service import ActionHandleService

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIService:

    def __init__(self):
        pass

    def handle_request(self, prompt, from_number):
        print(f"Usuario: {prompt}")

        # Crear una instancia de ActionHandleService
        action_handle_service = ActionHandleService(from_number, prompt)
        messages = action_handle_service.handle_actions()

        # Verificar si el mensaje es generado exclusivamente por BoxRequestAction o DistanceCalculationAction
        if len(messages) == 1:
            message_content = messages[0]["content"]
            if "distancia" in message_content or "¿Por favor, proporciona la dirección de entrega de la caja?" in message_content:
                # Retornar directamente el mensaje sin enviarlo a OpenAI
                return message_content

        # Enviar los mensajes a la API de OpenAI si no es una solicitud específica de distancia o caja
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, max_tokens=200, temperature=0.1  # type: ignore
        )

        # Obtener la respuesta generada por el modelo
        respuesta_modelo = response.choices[0].message.content.strip()  # type: ignore
    
        # Imprimir la respuesta generada por el modelo
        print(f"GPT: {respuesta_modelo}")

        # Guardar la conversión del modelo en la base de datos
        ConversacionRepo().crear_conversacion(prompt, respuesta_modelo, from_number)

        return respuesta_modelo
