# archivo: app/actions/box_request_action.py

from app.repositories.box_request_state_repo import BoxRequestStateRepo
from app.repositories.box_request_repo import BoxRequestRepo
from app.actions.distance_calculation_action import DistanceCalculationAction
from app.utils.date_converter import DateConverter
from datetime import datetime

class BoxRequestAction:
    ALLOWED_COUNTRIES = ["Honduras", "El Salvador", "Guatemala", "Nicaragua", "Mexico"]
    COST_PER_MILE = 1.0  # Costo por milla
    BASE_LOCATION = "107 Peach Lane, Schertz, Texas 78154"  # Dirección base de la empresa
    ENGANCHE = 30.0  # Costo de enganche fijo

    def __init__(self, user_id):
        self.user_id = user_id
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
            distance_action = DistanceCalculationAction()
            distance, cost = distance_action.calculate_distance_and_cost(prompt, self.BASE_LOCATION, self.COST_PER_MILE)

            if distance is None or cost is None:
                return "No se encontraron coordenadas para la dirección proporcionada. Por favor, verifica la dirección e inténtalo de nuevo."

            self.state["data"]["delivery_distance"] = distance
            self.state["data"]["delivery_cost"] = cost
            self.state["step"] = "ask_country"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])

            return (f"La distancia a la dirección de entrega es de aproximadamente {distance:.2f} millas. "
                    f"El costo adicional por entrega será de ${cost:.2f}. "
                    "¿A qué país deseas enviar la caja? Los países disponibles son: Honduras, El Salvador, Guatemala, Nicaragua, y México.")

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
                delivery_date = DateConverter.parse_date(prompt)
                self.state["data"]["delivery_date"] = delivery_date.strftime('%Y-%m-%d %H:%M:%S')
                self.state["step"] = "confirm"
                
                # Cálculo y asignación del costo total aquí para asegurar su disponibilidad
                total_cost = self.ENGANCHE + self.state["data"]["delivery_cost"]
                self.state["data"]["total_cost"] = total_cost

                BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])

                full_name = self.state["data"]["full_name"]
                address = self.state["data"]["address"]
                country = self.state["data"]["country"]
                destination_address = self.state["data"]["destination_address"]
                box_size = self.state["data"]["box_size"]
                delivery_cost = self.state["data"]["delivery_cost"]

                return (f"Resumen del pedido:\n"
                        f"Nombre del solicitante: {full_name}\n"
                        f"Dirección de entrega: {address}\n"
                        f"País de destino: {country}\n"
                        f"Dirección de destino: {destination_address}\n"
                        f"Tamaño de caja: {box_size}\n"
                        f"Fecha y hora de entrega: {self.state['data']['delivery_date']}\n"
                        f"Costo de entrega: ${delivery_cost:.2f}\n"
                        f"Enganche: ${self.ENGANCHE}\n"
                        f"**Costo total: ${total_cost:.2f}**\n"
                        "¿Deseas confirmar el pedido?")

            except ValueError:
                return "Error al procesar la fecha y hora de entrega. Usa un formato como 'hoy a las 8 pm' o 'mañana a las 12 pm'."

        elif step == "confirm":
            # Asegurarse de que `total_cost` esté disponible aquí sin errores
            delivery_date = datetime.strptime(self.state["data"]["delivery_date"], '%Y-%m-%d %H:%M:%S')
            BoxRequestRepo.create_box_request(
                customer_name=self.state["data"]["full_name"],
                address=self.state["data"]["address"],
                box_size=self.state["data"]["box_size"],
                delivery_date=delivery_date,
                engagement_fee=self.ENGANCHE,
                delivery_cost=self.state["data"]["delivery_cost"],
                total_cost=self.state["data"]["total_cost"],
                contact_number=self.user_id,
                country=self.state["data"]["country"],
                destination_address=self.state["data"]["destination_address"]
            )

            self.state = {"step": "start", "data": {}}
            BoxRequestStateRepo.delete_state(self.user_id)
            return "Pedido confirmado. Gracias por tu solicitud. Enviaremos una notificación con más detalles."
