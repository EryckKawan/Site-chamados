"""
Modelo para Armazenamento de Servidores
Sistema de monitoramento de capacidade e uso de disco
"""
from datetime import datetime

class ServidorStorage:
    """
    Classe que representa um servidor e seu armazenamento
    Realiza cálculos automáticos de conversão e porcentagens
    """
    
    def __init__(self, id=None, nome="", capacidade_valor=0, capacidade_unidade="GB", 
                 usado_valor=0, usado_unidade="GB", observacoes="", created_at=None):
        self.id = id
        self.nome = nome
        self.capacidade_valor = float(capacidade_valor)
        self.capacidade_unidade = capacidade_unidade
        self.usado_valor = float(usado_valor)
        self.usado_unidade = usado_unidade
        self.observacoes = observacoes
        self.created_at = created_at or datetime.now()
    
    def capacidade_em_gb(self):
        """
        Converte a capacidade total para GB
        Regra: 1 TB = 1024 GB
        """
        if self.capacidade_unidade.upper() == 'TB':
            return self.capacidade_valor * 1024
        return self.capacidade_valor
    
    def usado_em_gb(self):
        """
        Converte o espaço usado para GB
        Regra: 1 TB = 1024 GB
        """
        if self.usado_unidade.upper() == 'TB':
            return self.usado_valor * 1024
        return self.usado_valor
    
    def livre_em_gb(self):
        """
        Calcula o espaço livre em GB
        Fórmula: Livre = Capacidade - Usado
        """
        return self.capacidade_em_gb() - self.usado_em_gb()
    
    def percentual_uso(self):
        """
        Calcula a porcentagem de uso
        Fórmula: (Usado / Capacidade) * 100
        """
        capacidade = self.capacidade_em_gb()
        if capacidade == 0:
            return 0
        return (self.usado_em_gb() / capacidade) * 100
    
    def percentual_livre(self):
        """
        Calcula a porcentagem livre
        Fórmula: 100 - % Uso
        """
        return 100 - self.percentual_uso()
    
    def status_cor(self):
        """
        Retorna a cor do status baseado no uso
        Verde: < 70%
        Amarelo: 70% - 85%
        Vermelho: > 85%
        """
        uso = self.percentual_uso()
        if uso < 70:
            return 'success'
        elif uso < 85:
            return 'warning'
        return 'danger'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'capacidade_valor': self.capacidade_valor,
            'capacidade_unidade': self.capacidade_unidade,
            'usado_valor': self.usado_valor,
            'usado_unidade': self.usado_unidade,
            'capacidade_gb': round(self.capacidade_em_gb(), 2),
            'usado_gb': round(self.usado_em_gb(), 2),
            'livre_gb': round(self.livre_em_gb(), 2),
            'percentual_uso': round(self.percentual_uso(), 2),
            'percentual_livre': round(self.percentual_livre(), 2),
            'status_cor': self.status_cor(),
            'observacoes': self.observacoes
        }

