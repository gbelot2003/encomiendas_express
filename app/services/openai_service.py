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

        messages = []

        # Crear una instancia de ActionHandleService
        action_handle_service = ActionHandleService(from_number, prompt)
        messages.append = action_handle_service.handle_actions()

        # Si BoxRequestAction está activo, retornar exclusivamente su mensaje y evitar llamadas a OpenAI
        if ActionHandleService.box_request_active.get(from_number, False):
            return messages[0]["content"]


        messages.append({"role": "user", "content": prompt})


        # Enviar los mensajes a la API de OpenAI solo si BoxRequestAction no está activo
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
