# archivo: app/actions/box_request_action.py

from app.repositories.box_request_state_repo import BoxRequestStateRepo
from app.repositories.box_request_repo import BoxRequestRepo  # Importar el repositorio para guardar el pedido
from app.utils.date_converter import DateConverter  # Importar la clase de conversión

class BoxRequestAction:
    def __init__(self, user_id):
        self.user_id = user_id
        # Cargar estado desde la base de datos o inicializar si no existe
        saved_state = BoxRequestStateRepo.get_state(user_id)
        if saved_state:
            self.state = {"step": saved_state.step, "data": saved_state.data}
        else:
            self.state = {"step": "start", "data": {}}

    def handle_box_request(self, prompt):
        """Gestiona el flujo paso a paso para un pedido de caja."""
        step = self.state["step"]
        print(f"Current step: {step}, Received prompt: {prompt}")  # Depuración: Verificar el paso actual y el prompt recibido

        if step == "start":
            self.state["step"] = "ask_address"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            return "¿Por favor, proporciona la dirección de entrega de la caja?"

        elif step == "ask_address":
            # Guardamos la dirección proporcionada y pedimos el tamaño de la caja
            self.state["data"]["address"] = prompt
            self.state["step"] = "ask_box_size"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            print(f"Address saved: {self.state['data']['address']}")  # Depuración: Confirmar dirección guardada
            return "Gracias. ¿Qué tamaño de caja necesitas? Tenemos tamaños pequeña, mediana y grande."

        elif step == "ask_box_size":
            # Guardamos el tamaño de la caja y pedimos la fecha de entrega
            self.state["data"]["box_size"] = prompt
            self.state["step"] = "ask_delivery_date"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            print(f"Box size saved: {self.state['data']['box_size']}")  # Depuración: Confirmar tamaño de caja guardado
            return "Perfecto. ¿Cuál es la fecha y hora de entrega preferida?"

        elif step == "ask_delivery_date":
            # Guardamos la fecha de entrega y generamos el resumen del pedido
            self.state["data"]["delivery_date"] = prompt
            self.state["step"] = "confirm"
            BoxRequestStateRepo.update_state(self.user_id, self.state["step"], self.state["data"])
            print(f"Delivery date saved: {self.state['data']['delivery_date']}")  # Depuración: Confirmar fecha de entrega guardada

            # Generar resumen
            address = self.state["data"]["address"]
            box_size = self.state["data"]["box_size"]
            delivery_date = self.state["data"]["delivery_date"]
            return (f"Resumen del pedido:\n"
                    f"Dirección: {address}\n"
                    f"Tamaño de caja: {box_size}\n"
                    f"Fecha y hora de entrega: {delivery_date}\n"
                    f"Enganche de $30 USD. ¿Deseas confirmar el pedido?")

        elif step == "confirm":
            # Confirmamos el pedido, guardamos en box_request y limpiamos el estado de conversación
            print("Pedido confirmado.")  # Depuración: Confirmación final
            
            # Convertir delivery_date a un objeto datetime usando DateConverter
            try:
                delivery_date_str = self.state["data"]["delivery_date"]
                delivery_date = DateConverter.parse_date(delivery_date_str)
            except ValueError as e:
                print(f"Error en el formato de fecha: {e}")
                return "Error al procesar la fecha y hora de entrega. Asegúrate de usar un formato reconocible como 'hoy a las 8 pm' o 'mañana a las 12 pm'."

            # Guardar los datos en la tabla box_request
            BoxRequestRepo.create_box_request(
                customer_name="NombreCliente",  # Cambiar por el nombre del cliente si está disponible
                address=self.state["data"]["address"],
                box_size=self.state["data"]["box_size"],
                delivery_date=delivery_date,  # Usar el objeto datetime aquí
                engagement_fee=30.0,  # Enganche fijo de $30
                delivery_cost=0.0,  # Ajustar con el cálculo real del costo de entrega si es necesario
                total_cost=30.0,  # Total con el enganche
                contact_number="Contacto"  # Cambiar por el número de contacto si está disponible
            )
            
            # Reiniciar el estado
            self.state = {"step": "start", "data": {}}
            BoxRequestStateRepo.delete_state(self.user_id)  # Eliminar el estado de la conversación

            return "Pedido confirmado. Gracias por tu solicitud. Enviaremos una notificación con más detalles."