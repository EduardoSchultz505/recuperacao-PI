from . import db
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80))
    idade = db.Column(db.String(20))
    genero = db.Column(db.String(20))
    raca = db.Column(db.String(50))
    cor = db.Column(db.String(30))
    foto = db.Column(db.String(120))

    events = db.relationship('Event', backref='pet', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "idade": self.idade,
            "genero": self.genero,
            "raca": self.raca,
            "cor": self.cor,
            "foto": self.foto,
            "user_id": self.user_id
        }

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    data = db.Column(db.String(20), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "data": self.data,
            "pet_id": self.pet_id
        }
        
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    pets = db.relationship('Pet', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)