# archivo: app/repositories/box_request_repo.py

from app.models.box_request_model import BoxRequest
from app.extensions import db

class BoxRequestRepo:
    
    @staticmethod
    def create_box_request(customer_name, address, box_size, delivery_date, engagement_fee, delivery_cost, total_cost, contact_number, country, destination_address):
        """Crea una nueva solicitud de caja en la base de datos."""
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
            destination_address=destination_address
        )
        db.session.add(box_request)
        db.session.commit()
        return box_request

    @staticmethod
    def update_status(request_id, new_status):
        """Actualiza el estado de un pedido de caja."""
        box_request = BoxRequest.query.get(request_id)
        if box_request:
            box_request.status = new_status
            db.session.commit()
            return box_request
        else:
            return None

    @staticmethod
    def get_box_request_by_id(request_id):
        """Obtiene un pedido de caja por su ID."""
        return BoxRequest.query.get(request_id)

    @staticmethod
    def get_all_box_requests():
        """Obtiene todos los pedidos de caja."""
        return BoxRequest.query.all()

    @staticmethod
    def delete_box_request(request_id):
        """Elimina un pedido de caja por su ID."""
        box_request = BoxRequest.query.get(request_id)
        if box_request:
            db.session.delete(box_request)
            db.session.commit()
            return True
        return False
