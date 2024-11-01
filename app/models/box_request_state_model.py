# archivo: app/models/box_request_state_model.py

from app.extensions import db
from sqlalchemy.dialects.postgresql import JSON

class BoxRequestState(db.Model):
    __tablename__ = 'box_request_state'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, unique=True, nullable=False)
    step = db.Column(db.String(50), nullable=False)
    data = db.Column(JSON, nullable=True)  # Almacenará los datos de la conversación en formato JSON

    def __repr__(self):
        return f"<BoxRequestState(user_id={self.user_id}, step={self.step}, data={self.data})>"
