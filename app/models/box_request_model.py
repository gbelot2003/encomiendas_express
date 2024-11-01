# archivo: app/models/box_request_model.py

from app.extensions import db
from datetime import datetime

class BoxRequest(db.Model):
    __tablename__ = 'box_requests'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    box_size = db.Column(db.String(50), nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    engagement_fee = db.Column(db.Float, nullable=False)
    delivery_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    contact_number = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=False)  # Nueva columna
    destination_address = db.Column(db.String(255), nullable=False)  # Nueva columna

        # Nuevo campo para la fecha acordada de recogida
    agreed_pickup_date = db.Column(db.DateTime, nullable=True)  # Inicialmente NULL

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<BoxRequest {self.id} - {self.customer_name} - {self.status}>"
