from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Chamado(db.Model):
    __tablename__ = 'chamados'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(20), nullable=False, default='media')  # baixa, media, alta, critica
    status = db.Column(db.String(20), nullable=False, default='aberto')  # aberto, em_andamento, resolvido, fechado
    categoria = db.Column(db.String(50), nullable=False)  # hardware, software, rede, email, outros
    criado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    atribuido_para = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_resolucao = db.Column(db.DateTime, nullable=True)
    solucao = db.Column(db.Text, nullable=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('infraestrutura.id'), nullable=True)
    
    # Relacionamentos
    equipamento = db.relationship('Infraestrutura', backref='chamados')
    
    def __repr__(self):
        return f'<Chamado {self.id}: {self.titulo}>'
    
    @property
    def tempo_aberto(self):
        """Return a timedelta representing how long the ticket was open.

        Be tolerant: data_criacao and data_resolucao may be datetime objects or
        strings (coming from sqlite rows). Parse strings when necessary to
        avoid TypeError when subtracting.
        """
        def _to_dt(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                # Try common formats
                for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                try:
                    return datetime.fromisoformat(value)
                except Exception:
                    return None
            return None

        start = _to_dt(self.data_criacao)
        end = _to_dt(self.data_resolucao)

        if start is None:
            # Unknown start: return zero timedelta to be safe
            return timedelta(0)

        if end:
            return end - start
        return datetime.utcnow() - start
    
    @property
    def prioridade_class(self):
        classes = {
            'baixa': 'success',
            'media': 'warning', 
            'alta': 'danger',
            'critica': 'dark'
        }
        return classes.get(self.prioridade, 'secondary')
    
    @property
    def status_class(self):
        classes = {
            'aberto': 'primary',
            'em_andamento': 'warning',
            'resolvido': 'success',
            'fechado': 'secondary'
        }
        return classes.get(self.status, 'secondary')
