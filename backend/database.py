from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80))
    idade = db.Column(db.String(20))
    genero = db.Column(db.String(20))
    raca = db.Column(db.String(50))
    cor = db.Column(db.String(30))

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "idade": self.idade,
            "genero": self.genero,
            "raca": self.raca,
            "cor": self.cor
        }