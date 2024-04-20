from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Quarto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False, unique=True)
    capacidade_maxima = db.Column(db.Integer, nullable=False)
    valor_diaria = db.Column(db.Float, nullable=False)
    vago = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<Quarto {self.numero}>'

    def serialize(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'capacidade_maxima': self.capacidade_maxima,
            'valor_diaria': self.valor_diaria,
            'vago': self.vago
        }

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quarto_id = db.Column(db.Integer, db.ForeignKey('quarto.id', ondelete='CASCADE'), nullable=False)
    quarto = db.relationship('Quarto', backref=db.backref('reservas', lazy=True))
    data_checkin = db.Column(db.Date, nullable=False)
    data_checkout = db.Column(db.Date, nullable=False)
    numero_pessoas = db.Column(db.Integer, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id', ondelete='CASCADE'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('reservas', lazy=True))

    def serialize(self):
        if not self.cliente:
            raise ValueError("A reserva não pode ter um cliente desconhecido")
        
        return {
            'id':self.id,
            'quarto_id': self.quarto_id,
            'numero_quarto': self.quarto.numero,
            'data_checkin': self.data_checkin.isoformat(),
            'data_checkout': self.data_checkout.isoformat(), 
            'numero_pessoas': self.numero_pessoas,
            'cliente': {
                'id': self.cliente_id,
                'nome': self.cliente.nome,
                'sobrenome': self.cliente.sobrenome
            }
        }


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    celular = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Cliente {self.id}>'

    def serialize(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'sobrenome': self.sobrenome,
            'celular': self.celular,
            'email': self.email
        }
