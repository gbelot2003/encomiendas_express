# archivo: app/actions/box_request_action.py

class BoxRequestAction:
    def __init__(self, user_id):
        # Inicializamos el estado de la conversación del usuario
        self.user_id = user_id
        self.state = {
            "step": "start",
            "data": {}
        }

    def handle_box_request(self, prompt):
        # Flujo de conversación para solicitar una caja
        step = self.state["step"]

        if step == "start":
            self.state["step"] = "ask_address"
            return "¿Por favor, proporciona la dirección de entrega de la caja?"

        elif step == "ask_address":
            # Guardamos la dirección proporcionada y pedimos el tamaño de la caja
            self.state["data"]["address"] = prompt
            self.state["step"] = "ask_box_size"
            return "Gracias. ¿Qué tamaño de caja necesitas? Tenemos tamaños pequeña, mediana y grande."

        elif step == "ask_box_size":
            # Guardamos el tamaño de la caja y pedimos la fecha de entrega
            self.state["data"]["box_size"] = prompt
            self.state["step"] = "ask_delivery_date"
            return "Perfecto. ¿Cuál es la fecha y hora de entrega preferida?"

        elif step == "ask_delivery_date":
            # Guardamos la fecha de entrega y generamos el resumen del pedido
            self.state["data"]["delivery_date"] = prompt
            self.state["step"] = "confirm"

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
            # Confirmamos el pedido y limpiamos el estado de conversación
            self.state = {"step": "start", "data": {}}  # Reiniciar estado para futuras interacciones
            return "Pedido confirmado. Gracias por tu solicitud. Enviaremos una notificación con más detalles."

