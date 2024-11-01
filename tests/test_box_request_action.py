# archivo: tests/test_box_request_action.py

import unittest
from datetime import datetime, timezone
from app import create_app, db  # Importa la aplicación y la base de datos desde tu proyecto
from app.actions.box_request_action import BoxRequestAction
from app.actions.distance_calculation_action import DistanceCalculationAction
from app.repositories.box_request_repo import BoxRequestRepo
from app.data.pricing_data import pricing_data
from config import TestingConfig  # Importa la configuración adecuada
from unittest.mock import patch

class TestBoxRequestAction(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.app = create_app(config_class=TestingConfig)  # Usar configuración de prueba
        self.app_context = self.app.app_context()
        self.app_context.push()  # Empuja el contexto de la aplicación
        db.create_all()  # Crear todas las tablas para la base de datos en memoria

        self.user_id = "test_user"
        self.action = BoxRequestAction(self.user_id)
        self.ENGANCHE = 30.0  # Configurar el valor del enganche antes de usarlo

        # Simular datos iniciales en el estado para evitar interferencia con el flujo real
        self.initial_state = {
            "full_name": "Test User",
            "address": "123 Test St, Test City, TX",
            "country": "Honduras",
            "destination_address": "456 Destination St, Destination City",
            "box_size": "mediano",
            "linear_size": "60\"",
            "dimensions": "24\"x18\"x18\"",
            "box_price": 160.00,
            "engagement_fee": self.ENGANCHE,  # Usar una clave adecuada para el enganche
            "delivery_cost": 20.00,
            "delivery_date": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            "total_cost": 210.00
        }

    def tearDown(self):
        """Eliminar el contexto y los datos de prueba después de cada test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_initial_prompt(self):
        """Prueba el mensaje inicial de solicitud de nombre."""
        response = self.action.handle_box_request("solicitar caja")
        self.assertEqual(self.action.state["step"], "ask_name")
        self.assertIn("Por favor, proporciona tu nombre completo para el pedido.", response)

    def test_name_step(self):
        """Prueba el paso de solicitud de dirección después de proporcionar el nombre."""
        self.action.state["step"] = "ask_name"
        response = self.action.handle_box_request("Test User")
        self.assertEqual(self.action.state["step"], "ask_address")
        self.assertIn("Gracias. ¿Podrías proporcionar la dirección de entrega de la caja?", response)

    def test_address_step(self):
        """Prueba el cálculo de distancia y solicitud de país después de proporcionar la dirección."""
        self.action.state["step"] = "ask_address"
        with patch.object(DistanceCalculationAction, 'calculate_distance_and_cost', return_value=(10.0, 20.0)):
            response = self.action.handle_box_request(self.initial_state["address"])
            self.assertEqual(self.action.state["step"], "ask_country")
            self.assertIn("La distancia a la dirección de entrega es de aproximadamente", response)
            self.assertIn("¿A qué país deseas enviar la caja?", response)

    def test_country_selection(self):
        """Prueba la selección de país y muestra de tamaños disponibles."""
        self.action.state["step"] = "ask_country"
        response = self.action.handle_box_request("Honduras")
        self.assertEqual(self.action.state["step"], "ask_destination_address")
        
        # Verificar el contenido de available_sizes
        available_sizes = "\n".join(
            f'{size["tamaño"]} - {size["linear_size"]} ({size["dimensions"]}) - ${size["price"]:.2f}'
            for size in pricing_data["Honduras"]
        )
        print(f"Expected sizes:\n{available_sizes}")  # Añade este print para verificar en la salida
        print(f"Response:\n{response}")
        self.assertIn(available_sizes, response)

    def test_size_selection(self):
        """Prueba la selección de tamaño y confirmación de resumen."""
        self.action.state["data"]["country"] = "Honduras"  # Configura el país en el estado antes de seleccionar el tamaño
        self.action.state["step"] = "ask_box_size"
        response = self.action.handle_box_request("mediano")
        self.assertEqual(self.action.state["step"], "ask_delivery_date")
        self.assertIn("Tamaño seleccionado: mediano - 60\" (24\"x18\"x18\")", response)

    def test_delivery_date_step(self):
        """Prueba la configuración de fecha y generación de resumen."""
        self.action.state["data"] = self.initial_state
        self.action.state["step"] = "ask_delivery_date"
        response = self.action.handle_box_request("mañana a las 6:00 pm")
        
        # Verificar que el paso cambia a confirmación y se genera el resumen correctamente
        self.assertEqual(self.action.state["step"], "confirm")
        self.assertIn("Resumen del pedido:", response)
        self.assertIn("Tamaño de caja: mediano - 60\" (24\"x18\"x18\")", response)
        self.assertIn("Enganche: $30.00", response)  # Verificación del formato de enganche
        self.assertIn(f"**Costo total: ${self.action.state['data']['total_cost']:.2f}**", response)

        # Verificación de la fecha en formato legible
        delivery_date = datetime.strptime(self.action.state["data"]["delivery_date"], '%Y-%m-%d %H:%M:%S')
        formatted_date = delivery_date.strftime('%d de %B de %Y a las %I:%M %p')
        self.assertIn(f"Fecha y hora de entrega: {formatted_date}", response)

    def test_confirm_step(self):
        """Prueba la confirmación final y el guardado en la base de datos."""
        self.action.state["data"] = self.initial_state
        self.action.state["step"] = "confirm"
        response = self.action.handle_box_request("si")
        
        # Verificar que el estado se reinicia
        self.assertEqual(self.action.state["step"], "start")
        self.assertIn("Pedido confirmado. Gracias por tu solicitud.", response)
        
        # Verificar que se ha creado la solicitud en la base de datos
        box_request = BoxRequestRepo.get_box_request_by_id(self.user_id)
        self.assertIsNotNone(box_request)
        self.assertEqual(box_request.customer_name, "Test User")
        self.assertEqual(box_request.total_cost, self.initial_state["total_cost"])

if __name__ == "__main__":
    unittest.main()
