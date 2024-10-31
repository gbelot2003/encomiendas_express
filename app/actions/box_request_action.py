# archivo: app/actions/box_request_action.py

from app.repositories.box_request_state_repo import BoxRequestStateRepo

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
            # Confirmamos el pedido y limpiamos el estado de conversación
            print("Pedido confirmado.")  # Depuración: Confirmación final
            self.state = {"step": "start", "data": {}}  # Reiniciar estado para futuras interacciones
            BoxRequestStateRepo.delete_state(self.user_id)  # Eliminar el estado de la conversación
            return "Pedido confirmado. Gracias por tu solicitud. Enviaremos una notificación con más detalles."
