from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Worker(UserMixin, db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    expiry_date = db.Column(db.Date)
    price = db.Column(db.Numeric(10, 2), default=0)
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id', ondelete='CASCADE'))
    worker_id = db.Column(db.String(10), db.ForeignKey('worker.id', ondelete='CASCADE'), nullable=True)
    quantity = db.Column(db.Integer)
    type = db.Column(db.Enum('buy', 'sell'))
    price = db.Column(db.Numeric(10, 2), default=0)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    # ✅ relationships
    medicine = db.relationship('Medicine', backref=db.backref('transactions', cascade='all, delete'))
    worker = db.relationship('Worker', backref='transactions', foreign_keys=[worker_id])
