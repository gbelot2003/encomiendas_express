# app/services/answer_service.py

import random


def answer_yes_no(name, age, day, question):
    responses = ["sí", "no"]
    
    answer = random.choice(responses)

    
    return (f"EL Oraculo dice que para {name}, con {age} años y para el día {day}, la respuesta a la pregunta {question}, la respuesta es {answer}")
    #return answer