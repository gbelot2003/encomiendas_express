# src/services/openai_service.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from app.repositories.conversaion_repo import ConversacionRepo

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIService:

    def __init__(self):
        pass

    def handle_request(self, prompt, from_number):
        print(f"Usuario: {prompt}")

        # Enviar el mensaje a GPT y devolver la respuesta
        messages = [{"role": "user", "content": prompt}]

        # Enviar los mensajes a la API de OpenAI
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