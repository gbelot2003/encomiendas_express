# app/repositories/contact_repo.py
from app.extensions import db
from app.models.contact_model import Contact as Contacto

class ContactRepo:
    @staticmethod
    def crear_contacto(telefono, nombre=None, direccion=None, email=None):
        nuevo_contacto = Contacto(nombre=nombre, telefono=telefono, direccion=direccion, email=email)
        db.session.add(nuevo_contacto)
        db.session.commit()
        return nuevo_contacto

    @staticmethod
    def obtener_contacto_por_telefono(telefono):
        return Contacto.query.filter_by(telefono=telefono).first()

    @staticmethod
    def obtener_todos_contactos():
        return Contacto.query.all()

    @staticmethod
    def actualizar_contacto(contacto_id, nombre=None, telefono=None, direccion=None, email=None):
        contacto = Contacto.query.filter_by(id=contacto_id).first()
        if contacto:
            if nombre:
                contacto.nombre = nombre
            if telefono:
                contacto.telefono = telefono
            if direccion:
                contacto.direccion = direccion
            if email:
                contacto.email = email
            db.session.commit()
        return contacto

    @staticmethod
    def eliminar_contacto(contacto_id):
        contacto = Contacto.query.filter_by(id=contacto_id).first()
        if contacto:
            db.session.delete(contacto)
            db.session.commit()
        return contacto