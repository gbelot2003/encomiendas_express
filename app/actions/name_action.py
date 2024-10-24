# app/actions/name_action.py

from app.extractors.name_extractor import NombreExtractor
from app.repositories.contact_repo import ContactRepo
import logging

class NameAction:
    def __init__(self, contacto, prompt):
        self.contacto = contacto
        self.prompt = prompt

    def process_name(self):
        message = None
        # Si el contacto tiene un nombre, usarlo en la conversación
        if self.contacto.nombre:
            message = {"role": "assistant", "content": f"El usuario se llama y llamalo {self.contacto.nombre}."}
        else:
            extraerNombre = NombreExtractor().extraer_nombre(self.prompt)            # grabar nombre en base de datos
            if extraerNombre:
                ContactRepo().actualizar_contacto(self.contacto.id, nombre=extraerNombre)
                message = {"role": "assistant", "content": f"El usuario se llama y llamalo {extraerNombre}."}
            else:
                message = {"role": "system", "content": "pregunte al usuario en que le podemos ayudar y cual es su nombre para mejor servicio."}
        return message