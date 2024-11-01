# tests/test_box_request_action.py

import unittest
from datetime import datetime, timezone
from app import create_app  # Asegúrate de que `create_app` sea tu función de fábrica para Flask
from app.actions.box_request_action import BoxRequestAction

class TestBoxRequestActionSummary(unittest.TestCase):
    def setUp(self):
        self.app = create_app()  # Crear la aplicación
        self.app_context = self.app.app_context()  # Crear un contexto de aplicación
        self.app_context.push()  # Iniciar el contexto de aplicación
        
        self.user_id = "test_user"
        self.action = BoxRequestAction(self.user_id)
        
        # Simular datos en el estado para probar el resumen
        self.action.state["data"] = {
            "full_name": "Gerardo Belot",
            "address": "11135 Beverly Hills Dr, Helotes, TX 78023, USA",
            "country": "Honduras",
            "destination_address": "CP 1101, Avenida Sierra Nevada # 822, San Salvador, El Salvador",
            "box_size": "mediano",
            "linear_size": "60\"",
            "dimensions": "24\"x18\"x18\"",
            "box_price": 160.00,
            "delivery_cost": 27.36,
            "delivery_date": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        }
        self.action.ENGANCHE = 30.0
        self.action.state["data"]["total_cost"] = (
            self.action.state["data"]["box_price"] + self.action.state["data"]["delivery_cost"] + self.action.ENGANCHE
        )
    
    def tearDown(self):
        self.app_context.pop()  # Eliminar el contexto de aplicación al final de la prueba
    
    def test_summary_generation(self):
        # Generar el resumen
        summary = self.action.generate_summary()

        # Verificar partes del resumen
        self.assertIn("Resumen del pedido:", summary)
        self.assertIn("Nombre del solicitante: Gerardo Belot", summary)
        self.assertIn("Dirección de entrega: 11135 Beverly Hills Dr, Helotes, TX 78023, USA", summary)
        self.assertIn("País de destino: Honduras", summary)
        self.assertIn("Dirección de destino: CP 1101, Avenida Sierra Nevada # 822, San Salvador, El Salvador", summary)
        self.assertIn("Tamaño de caja: mediano - 60\" (24\"x18\"x18\")", summary)
        self.assertIn("Costo de caja: $160.00", summary)
        self.assertIn("Costo de entrega: $27.36", summary)
        self.assertIn("Enganche: $30.00", summary)
        self.assertIn(f"**Costo total: ${self.action.state['data']['total_cost']:.2f}**", summary)
        
        # Comprobar que la fecha y hora están en un formato legible
        expected_date = datetime.strptime(self.action.state["data"]["delivery_date"], '%Y-%m-%d %H:%M:%S')
        formatted_date = expected_date.strftime('%d de %B de %Y a las %I:%M %p')
        self.assertIn(f"Fecha y hora de entrega: {formatted_date}", summary)

if __name__ == "__main__":
    unittest.main()
