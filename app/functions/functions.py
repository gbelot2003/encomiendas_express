# functions.py
functions = [
    {
        "name": "answer_yes_no",
        "description": "Responde con 'sí' o 'no' a una pregunta.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "El nombre de la persona."},
                "age": {"type": "number", "description": "La edad de la persona."},
                "day": {"type": "string", "description": "El día de la semana."},
                "question": {"type": "string", "description": "La pregunta a la que se debe responder."}
            },
            "required": ["name", "age", "day","question"]
        }
    }
]

system_message = {"role": "system", "content": "Eres un asistente útil. Si el usuario no proporciona todos los parámetros necesarios para una función, pídele que proporcione los parámetros faltantes."}