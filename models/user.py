from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, user, tech
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    chamados_criados = db.relationship('Chamado', backref='criador', lazy=True, foreign_keys='Chamado.criado_por')
    chamados_atribuidos = db.relationship('Chamado', backref='tecnico', lazy=True, foreign_keys='Chamado.atribuido_para')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_tech(self):
        return self.role in ['admin', 'tech']

