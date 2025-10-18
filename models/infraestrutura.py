from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Infraestrutura(db.Model):
    __tablename__ = 'infraestrutura'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # computador, impressora, servidor, roteador, etc.
    marca = db.Column(db.String(50), nullable=True)
    modelo = db.Column(db.String(100), nullable=True)
    numero_serie = db.Column(db.String(100), nullable=True)
    localizacao = db.Column(db.String(100), nullable=False)  # sala, andar, prédio
    responsavel = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='ativo')  # ativo, inativo, manutencao
    data_aquisicao = db.Column(db.Date, nullable=True)
    data_ultima_manutencao = db.Column(db.Date, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Infraestrutura {self.id}: {self.nome}>'
    
    @property
    def status_class(self):
        classes = {
            'ativo': 'success',
            'inativo': 'danger',
            'manutencao': 'warning'
        }
        return classes.get(self.status, 'secondary')
    
    @property
    def tipo_icon(self):
        icons = {
            'computador': '💻',
            'impressora': '🖨️',
            'servidor': '🖥️',
            'roteador': '📡',
            'switch': '🔌',
            'telefone': '📞',
            'monitor': '🖥️',
            'outros': '⚙️'
        }
        return icons.get(self.tipo.lower(), '⚙️')

