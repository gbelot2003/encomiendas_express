import unittest
from datetime import datetime, timezone
from app.repositories.box_request_repo import BoxRequestRepo
from app.extensions import db
from app.models.box_request_model import BoxRequest
from app import create_app
from config import TestingConfig  # Importa la configuración adecuada

class TestBoxRequestRepo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configurar la aplicación en el contexto de pruebas
        cls.app = create_app(config_class=TestingConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        # Limpiar la base de datos antes de cada prueba
        BoxRequest.query.delete()
        db.session.commit()

    def test_create_box_request_with_default_pickup_date(self):
        # Crear una solicitud de caja sin agreed_pickup_date
        box_request = BoxRequestRepo.create_box_request(
            customer_name="Gerardo Belot",
            address="11135 Beverly Hills Dr, Helotes, TX 78023, USA",
            box_size="mediano",
            delivery_date=datetime(2024, 11, 1, 10, 0),
            engagement_fee=30.0,
            delivery_cost=25.0,
            total_cost=85.0,
            contact_number="555-1234",
            country="Honduras",
            destination_address="CP 1101, Avenida Sierra Nevada # 822, San Salvador, El Salvador"
        )
        # Verificar que se haya creado y agreed_pickup_date sea None
        self.assertIsNotNone(box_request)
        self.assertIsNone(box_request.agreed_pickup_date)
        self.assertEqual(box_request.customer_name, "Gerardo Belot")

    def test_create_box_request_with_specified_pickup_date(self):
        # Crear una solicitud de caja con una agreed_pickup_date específica
        agreed_pickup_date = datetime(2024, 11, 2, 15, 0)
        box_request = BoxRequestRepo.create_box_request(
            customer_name="Gerardo Belot",
            address="11135 Beverly Hills Dr, Helotes, TX 78023, USA",
            box_size="grande",
            delivery_date=datetime(2024, 11, 1, 10, 0),
            engagement_fee=30.0,
            delivery_cost=25.0,
            total_cost=85.0,
            contact_number="555-1234",
            country="Honduras",
            destination_address="CP 1101, Avenida Sierra Nevada # 822, San Salvador, El Salvador",
            agreed_pickup_date=agreed_pickup_date
        )
        # Verificar que agreed_pickup_date sea la fecha especificada
        self.assertEqual(box_request.agreed_pickup_date, agreed_pickup_date)

    def test_update_agreed_pickup_date(self):
        # Crear una solicitud de caja inicial
        box_request = BoxRequestRepo.create_box_request(
            customer_name="Gerardo Belot",
            address="11135 Beverly Hills Dr, Helotes, TX 78023, USA",
            box_size="pequeño",
            delivery_date=datetime(2024, 11, 1, 10, 0),
            engagement_fee=30.0,
            delivery_cost=25.0,
            total_cost=85.0,
            contact_number="555-1234",
            country="Honduras",
            destination_address="CP 1101, Avenida Sierra Nevada # 822, San Salvador, El Salvador"
        )
        
        # Actualizar agreed_pickup_date
        new_pickup_date = datetime(2024, 11, 3, 9, 0)
        updated_box_request = BoxRequestRepo.update_agreed_pickup_date(box_request.id, new_pickup_date)
        
        # Verificar que la fecha se haya actualizado correctamente
        self.assertEqual(updated_box_request.agreed_pickup_date, new_pickup_date)

if __name__ == "__main__":
    unittest.main()
