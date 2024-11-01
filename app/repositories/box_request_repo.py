# archivo: app/repositories/box_request_repo.py

from app.models.box_request_model import BoxRequest
from app.extensions import db

class BoxRequestRepo:
    
    @staticmethod
    def create_box_request(customer_name, address, box_size, delivery_date, engagement_fee, delivery_cost, total_cost, contact_number, country, destination_address, agreed_pickup_date=None):
        """Crea una nueva solicitud de caja en la base de datos, con agreed_pickup_date inicialmente en None."""
        box_request = BoxRequest(
            customer_name=customer_name,
            address=address,
            box_size=box_size,
            delivery_date=delivery_date,
            engagement_fee=engagement_fee,
            delivery_cost=delivery_cost,
            total_cost=total_cost,
            contact_number=contact_number,
            country=country,
            destination_address=destination_address,
            agreed_pickup_date=agreed_pickup_date  # Inicialmente None, se puede actualizar después
        )
        db.session.add(box_request)
        db.session.commit()
        return box_request

    @staticmethod
    def update_status(request_id, new_status):
        """Actualiza el estado de un pedido de caja."""
        box_request = db.session.get(BoxRequest, request_id)  # Cambiado a db.session.get
        if box_request:
            box_request.status = new_status
            db.session.commit()
            return box_request
        return None

    @staticmethod
    def update_agreed_pickup_date(request_id, pickup_date):
        """Actualiza el campo agreed_pickup_date de un pedido de caja."""
        box_request = BoxRequest.query.get(request_id)
        if box_request:
            box_request.agreed_pickup_date = pickup_date
            db.session.commit()
            return box_request
        return None

    @staticmethod
    def get_box_request_by_id(request_id):
        """Obtiene un pedido de caja por su ID."""
        return db.session.get(BoxRequest, request_id)  # Cambiado a db.session.get

    @staticmethod
    def get_all_box_requests():
        """Obtiene todos los pedidos de caja."""
        return BoxRequest.query.all()

    @staticmethod
    def delete_box_request(request_id):
        """Elimina un pedido de caja por su ID."""
        box_request = db.session.get(BoxRequest, request_id)
        if box_request:
            db.session.delete(box_request)
            db.session.commit()
            return True
        return False
