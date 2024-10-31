# archivo: app/repositories/box_request_state_repo.py

from app.models.box_request_state_model import BoxRequestState
from app.extensions import db

class BoxRequestStateRepo:
    
    @staticmethod
    def get_state(user_id):
        """Obtiene el estado del flujo de conversación de un usuario específico."""
        return BoxRequestState.query.filter_by(user_id=user_id).first()

    @staticmethod
    def update_state(user_id, step, data):
        """Actualiza o crea el estado del flujo de conversación de un usuario."""
        state = BoxRequestStateRepo.get_state(user_id)
        if state:
            state.step = step
            state.data = data
        else:
            state = BoxRequestState(user_id=user_id, step=step, data=data)
            db.session.add(state)
        db.session.commit()
        return state

    @staticmethod
    def delete_state(user_id):
        """Elimina el estado de un usuario una vez que se completa el flujo."""
        state = BoxRequestStateRepo.get_state(user_id)
        if state:
            db.session.delete(state)
            db.session.commit()
        return state
