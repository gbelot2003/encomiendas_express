# archivo: app/actions/box_request_action.py

from app.repositories.box_request_state_repo import BoxRequestStateRepo
from app.repositories.box_request_repo import BoxRequestRepo
from app.actions.distance_calculation_action import DistanceCalculationAction
from app.utils.date_converter import DateConverter
from app.data.pricing_data import pricing_data
from datetime import datetime
from app.extensions import db

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

    def generate_summary(self):
        """Genera un resumen detallado del pedido."""
        total_cost = (
            self.state["data"].get("box_price", 0) + 
            self.state["data"].get("delivery_cost", 0) + 
            self.ENGANCHE
        )
        delivery_date = datetime.strptime(self.state["data"]["delivery_date"], '%Y-%m-%d %H:%M:%S')
        formatted_date = delivery_date.strftime('%d de %B de %Y a las %I:%M %p')

        return (f"Resumen del pedido:\n"
                f"Nombre del solicitante: {self.state['data'].get('full_name')}\n"
                f"Dirección de entrega: {self.state['data'].get('address')}\n"
                f"País de destino: {self.state['data'].get('country')}\n"
                f"Dirección de destino: {self.state['data'].get('destination_address', 'No proporcionada')}\n"
                f"Tamaño de caja: {self.state['data'].get('box_size')} - {self.state['data'].get('linear_size')} "
                f"({self.state['data'].get('dimensions')})\n"
                f"Costo de caja: ${self.state['data'].get('box_price', 0):.2f}\n"
                f"Costo de entrega: ${self.state['data'].get('delivery_cost', 0):.2f}\n"
                f"Enganche: ${self.ENGANCHE:.2f}\n"  # Aseguramos que siempre tenga dos decimales
                f"Fecha y hora de entrega: {formatted_date}\n"
                f"**Costo total: ${total_cost:.2f}**\n"
                "¿Deseas confirmar el pedido?")

    def get_available_sizes_for_country(self, country):
        """Devuelve las opciones de tamaño y precio según el país."""
        if country in pricing_data:
            options = pricing_data[country]
            options_text = "\n".join(
                [f"{opt['tamaño']} - {opt['linear_size']} ({opt['dimensions']}) - ${opt['price']:.2f}" for opt in options]
            )
            return f"Tamaños disponibles para {country}:\n{options_text}\nPor favor, elige un tamaño."
        else:
            return "País no disponible para envíos."

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
            self.state["step"] = "ask_country"  # Asegúrate de que esta línea se ejecute
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])

            return (f"La distancia a la dirección de entrega es de aproximadamente {distance:.2f} millas. "
                    f"El costo adicional por entrega será de ${cost:.2f}. "
                    "¿A qué país deseas enviar la caja? Los países disponibles son: Honduras, El Salvador, Guatemala, Nicaragua, y México.")

        elif step == "ask_country":
            if prompt not in self.ALLOWED_COUNTRIES:
                return "País no válido. Por favor, elige uno de los siguientes: Honduras, El Salvador, Guatemala, Nicaragua, o México."

            # Guardar el país seleccionado en el estado
            self.state["data"]["country"] = prompt

            # Obtener los tamaños disponibles para el país
            available_sizes = self.get_available_sizes_for_country(prompt)

            # Cambia al paso "ask_destination_address" después de mostrar los tamaños
            self.state["step"] = "ask_destination_address"

            # Guardar el estado actualizado
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])

            # Retornar el mensaje con los tamaños disponibles en el país seleccionado
            return available_sizes

        elif step == "ask_destination_address":
            self.state["data"]["destination_address"] = prompt
            self.state["step"] = "ask_box_size"
            selected_country = self.state["data"]["country"]
            available_sizes = self.get_available_sizes_for_country(selected_country)
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            return available_sizes

        elif step == "ask_box_size":
            selected_country = self.state["data"]["country"]
            selected_size = next(
                (opt for opt in pricing_data[selected_country]
                 if opt["linear_size"] == prompt or opt["tamaño"].lower() == prompt.lower()),
                None
            )

            if selected_size:
                self.state["data"].update({
                    "box_size": selected_size["tamaño"],
                    "linear_size": selected_size["linear_size"],
                    "dimensions": selected_size["dimensions"],
                    "box_price": selected_size["price"]
                })
                self.state["step"] = "ask_delivery_date"
                BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])

                return (f"Tamaño seleccionado: {selected_size['tamaño']} - {selected_size['linear_size']} ({selected_size['dimensions']}) - "
                        f"Precio: ${selected_size['price']:.2f}. Ahora, proporciona la fecha y hora de entrega preferida.")
            
            return "Tamaño no válido. Por favor, elige un tamaño de la lista proporcionada."

        elif step == "ask_delivery_date":
            try:
                delivery_date = DateConverter.parse_date(prompt)
                self.state["data"]["delivery_date"] = delivery_date.strftime('%Y-%m-%d %H:%M:%S')
                self.state["step"] = "confirm"
                
                total_cost = self.ENGANCHE + self.state["data"]["delivery_cost"] + self.state["data"]["box_price"]
                self.state["data"]["total_cost"] = total_cost

                BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
                
                # Formato de fecha y hora legible para humanos
                def format_human_readable_datetime(date_str):
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        return date_obj.strftime('%d de %B de %Y a las %I:%M %p')
                    except ValueError:
                        return date_str  # En caso de error, devolver el valor original
        
                return (f"Resumen del pedido:\n"
                        f"Nombre del solicitante: {self.state['data']['full_name']}\n"
                        f"Dirección de entrega: {self.state['data']['address']}\n"
                        f"País de destino: {self.state['data']['country']}\n"
                        f"Dirección de destino: {self.state['data'].get('destination_address', 'No proporcionada')}\n"  # Uso de .get para prevenir KeyError
                        f"Tamaño de caja: {self.state['data']['box_size']} - {self.state['data']['linear_size']} "
                        f"({self.state['data']['dimensions']})\n"
                        f"Costo de caja: ${self.state['data']['box_price']:.2f}\n"
                        f"Costo de entrega: ${self.state['data']['delivery_cost']:.2f}\n"
                        f"Enganche: ${self.ENGANCHE:.2f}\n"
                        f"Fecha y hora de entrega: {format_human_readable_datetime(self.state['data']['delivery_date'])}\n"
                        f"**Costo total: ${total_cost:.2f}**\n"
                        "¿Deseas confirmar el pedido?")

            except ValueError:
                return "Error al procesar la fecha y hora de entrega. Usa un formato como 'hoy a las 8 pm' o 'mañana a las 12 pm'."

        elif step == "confirm":
            delivery_date = datetime.strptime(self.state["data"]["delivery_date"], '%Y-%m-%d %H:%M:%S')

            try:
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
                    destination_address=self.state["data"].get("destination_address", "No proporcionada")
                )
            except Exception as e:
                print("Error al crear el pedido en la base de datos:", e)

            db.session.commit()  # <-- Asegúrate de que la transacción se confirme
            self.state = {"step": "start", "data": {}}
            BoxRequestStateRepo.delete_state(self.user_id)
            return "Pedido confirmado. Gracias por tu solicitud. Enviaremos una notificación con más detalles."