import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.functions.functions import functions, system_message
from app.services.answer_service import answer_yes_no

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAlternativeService:
    
    def __init__(self):
        self.parameters = {}

    def handle_request(self, prompt, from_number):
        print(f"Usuario: {prompt}")
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        # Enviar los mensajes a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=messages, 
            functions=functions,
            function_call="auto",
            max_tokens=200, 
            temperature=0.1
        )

        response_message = response.choices[0].message

        if hasattr(response_message, "function_call") and response_message.function_call is not None:
            function_call = response_message.function_call
            function_name = function_call.name
            function_args = json.loads(function_call.arguments)

            if function_name == "answer_yes_no":
                name = function_args.get("name")
                age = function_args.get("age")
                day = function_args.get("day")
                question = function_args.get("question")

                # Check if any required parameters are missing
                missing_params = []
                if not name:
                    missing_params.append("name")
                if not age:
                    missing_params.append("age")
                if not day:
                    missing_params.append("day")
                if not question:
                    missing_params.append("question")

                if missing_params:
                    # Ask for the first missing parameter
                    first_missing_param = missing_params[0]
                    respuesta_modelo = f"Por favor, proporciona el parámetro: {first_missing_param}."
                else:
                    respuesta_modelo = answer_yes_no(name, age, day, question)
            else:
                respuesta_modelo = "No se pudo procesar la función."
        else:
            print(f"GPT: None")
            respuesta_modelo = response_message.content.strip() if hasattr(response_message, "content") else "No content in response"

        return respuesta_modelo

    def update_parameters(self, param_name, param_value):
        self.parameters[param_name] = param_value

    def get_parameters(self):
        return self.parameters