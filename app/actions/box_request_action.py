# archivo: app/actions/box_request_action.py

from app.repositories.box_request_state_repo import BoxRequestStateRepo
from app.repositories.box_request_repo import BoxRequestRepo
from app.utils.date_converter import DateConverter
from datetime import datetime

class BoxRequestAction:
    ALLOWED_COUNTRIES = ["Honduras", "El Salvador", "Guatemala", "Nicaragua", "Mexico"]

    def __init__(self, user_id):
        self.user_id = user_id  # Usamos user_id directamente para contact_number
        saved_state = BoxRequestStateRepo.get_state(user_id)
        if saved_state:
            self.state = {"step": saved_state.step, "data": saved_state.data}
        else:
            self.state = {"step": "start", "data": {}}


    def handle_box_request(self, prompt):
        step = self.state["step"]
        print(f"Current step: {step}, Received prompt: {prompt}")

        if step == "start":
            self.state["step"] = "ask_name"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            return "Por favor, proporciona tu nombre completo para el pedido."

        elif step == "ask_name":
            self.state["data"]["full_name"] = prompt
            self.state["step"] = "ask_address"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            return "Gracias. ¿Podrías proporcionar la dirección de entrega de la caja?"

        elif step == "ask_address":
            self.state["data"]["address"] = prompt
            self.state["step"] = "ask_country"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            return "¿A qué país deseas enviar la caja? Los países disponibles son: Honduras, El Salvador, Guatemala, Nicaragua, y México."

        elif step == "ask_country":
            if prompt not in self.ALLOWED_COUNTRIES:
                return "País no válido. Por favor, elige uno de los siguientes: Honduras, El Salvador, Guatemala, Nicaragua, o México."

            self.state["data"]["country"] = prompt
            self.state["step"] = "ask_destination_address"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            return "Proporciónanos la dirección completa de destino en el país seleccionado."

        elif step == "ask_destination_address":
            self.state["data"]["destination_address"] = prompt
            self.state["step"] = "ask_box_size"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            return "Gracias. ¿Qué tamaño de caja necesitas? Tenemos tamaños pequeña, mediana y grande."

        elif step == "ask_box_size":
            self.state["data"]["box_size"] = prompt
            self.state["step"] = "ask_delivery_date"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            return "Perfecto. ¿Cuál es la fecha y hora de entrega preferida?"

        elif step == "ask_delivery_date":
            try:
                # Convertimos la fecha a cadena antes de guardarla
                delivery_date = DateConverter.parse_date(prompt)
                self.state["data"]["delivery_date"] = delivery_date.strftime('%Y-%m-%d %H:%M:%S')
                self.state["step"] = "confirm"
                BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])

                full_name = self.state["data"]["full_name"]
                address = self.state["data"]["address"]
                country = self.state["data"]["country"]
                destination_address = self.state["data"]["destination_address"]
                box_size = self.state["data"]["box_size"]

                return (f"Resumen del pedido:\n"
                        f"Nombre del solicitante: {full_name}\n"
                        f"Dirección de entrega: {address}\n"
                        f"País de destino: {country}\n"
                        f"Dirección de destino: {destination_address}\n"
                        f"Tamaño de caja: {box_size}\n"
                        f"Fecha y hora de entrega: {self.state['data']['delivery_date']}\n"
                        f"Enganche de $30 USD. ¿Deseas confirmar el pedido?")

            except ValueError:
                return "Error al procesar la fecha y hora de entrega. Usa un formato como 'hoy a las 8 pm' o 'mañana a las 12 pm'."

        elif step == "confirm":
            # Convertimos la fecha de cadena a datetime al guardar el pedido
            delivery_date = datetime.strptime(self.state["data"]["delivery_date"], '%Y-%m-%d %H:%M:%S')
            BoxRequestRepo.create_box_request(
                customer_name=self.state["data"]["full_name"],
                address=self.state["data"]["address"],
                box_size=self.state["data"]["box_size"],
                delivery_date=delivery_date,
                engagement_fee=30.0,
                delivery_cost=0.0,
                total_cost=30.0,
                contact_number=self.user_id,  # Usamos user_id como contact_number
                country=self.state["data"]["country"],
                destination_address=self.state["data"]["destination_address"]
            )

            print("Pedido confirmado y guardado en la base de datos.")
            self.state = {"step": "start", "data": {}}
            BoxRequestStateRepo.delete_state(self.user_id)
            return "Pedido confirmado. Gracias por tu solicitud. Enviaremos una notificación con más detalles."
