from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Servidor(db.Model):
    __tablename__ = 'servidores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=True)
    ip_endereco = db.Column(db.String(50), nullable=True)
    sistema_operacional = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com armazenamentos
    armazenamentos = db.relationship('Armazenamento', backref='servidor', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Servidor {self.nome}>'

    @property
    def total_armazenamentos(self):
        return len(self.armazenamentos)

    @property
    def capacidade_total_gb(self):
        total = 0
        for arm in self.armazenamentos:
            total += arm.capacidade_gb
        return round(total, 2)

    @property
    def usado_total_gb(self):
        total = 0
        for arm in self.armazenamentos:
            total += arm.usado_gb
        return round(total, 2)

    @property
    def livre_total_gb(self):
        return round(self.capacidade_total_gb - self.usado_total_gb, 2)

    @property
    def percentual_uso_total(self):
        if self.capacidade_total_gb == 0:
            return 0.0
        return round((self.usado_total_gb / self.capacidade_total_gb) * 100, 2)

    @property
    def status_cor_total(self):
        if self.percentual_uso_total < 70:
            return 'success'
        elif self.percentual_uso_total < 85:
            return 'warning'
        return 'danger'


class Armazenamento(db.Model):
    __tablename__ = 'armazenamentos'

    id = db.Column(db.Integer, primary_key=True)
    servidor_id = db.Column(db.Integer, db.ForeignKey('servidores.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'SSD', 'HDD', 'NVMe', etc.
    capacidade_valor = db.Column(db.Float, nullable=False)
    capacidade_unidade = db.Column(db.String(10), nullable=False)  # 'GB' ou 'TB'
    usado_valor = db.Column(db.Float, nullable=False)
    usado_unidade = db.Column(db.String(10), nullable=False)  # 'GB' ou 'TB'
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Armazenamento {self.nome} do {self.servidor.nome}>'

    def _to_gb(self, valor, unidade):
        if unidade.upper() == 'TB':
            return valor * 1024
        elif unidade.upper() == 'MB':
            return valor / 1024
        return valor

    @property
    def capacidade_gb(self):
        return round(self._to_gb(self.capacidade_valor, self.capacidade_unidade), 2)

    @property
    def usado_gb(self):
        return round(self._to_gb(self.usado_valor, self.usado_unidade), 2)

    @property
    def livre_gb(self):
        return round(self.capacidade_gb - self.usado_gb, 2)

    @property
    def percentual_uso(self):
        if self.capacidade_gb == 0:
            return 0.0
        return round((self.usado_gb / self.capacidade_gb) * 100, 2)

    @property
    def percentual_livre(self):
        return round(100 - self.percentual_uso, 2)

    @property
    def status_cor(self):
        if self.percentual_uso < 70:
            return 'success'
        elif self.percentual_uso < 85:
            return 'warning'
        return 'danger'

    @property
    def tipo_icone(self):
        icons = {
            'SSD': 'bi-hdd-ssd',
            'HDD': 'bi-hdd',
            'NVMe': 'bi-cpu',
            'SAS': 'bi-hdd-rack'
        }
        return icons.get(self.tipo.upper(), 'bi-hdd')
