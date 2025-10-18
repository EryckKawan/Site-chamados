from datetime import datetime

class Servidor:
    """Modelo para representar um servidor e seu armazenamento."""
    
    # Fatores de conversão entre unidades
    CONVERSOES = {
        'MB': {'MB': 1, 'GB': 1/1024, 'TB': 1/(1024*1024)},
        'GB': {'MB': 1024, 'GB': 1, 'TB': 1/1024},
        'TB': {'MB': 1024*1024, 'GB': 1024, 'TB': 1}
    }
    
    def __init__(self, id=None, nome=None, ip=None, localizacao=None, 
                 espaco_total=0, espaco_usado=0, unidade='GB', 
                 observacoes=None, created_at=None, updated_at=None):
        self.id = id
        self.nome = nome
        self.ip = ip
        self.localizacao = localizacao
        self.espaco_total = espaco_total
        self.espaco_usado = espaco_usado
        self.unidade = unidade  # MB, GB, TB
        self.observacoes = observacoes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @staticmethod
    def converter_unidade(valor, unidade_origem, unidade_destino):
        """
        Converte um valor de uma unidade para outra.
        
        Exemplo:
            Servidor.converter_unidade(500, 'GB', 'TB')  # Retorna 0.48828125
            Servidor.converter_unidade(2, 'TB', 'GB')    # Retorna 2048
        """
        if unidade_origem not in Servidor.CONVERSOES or unidade_destino not in Servidor.CONVERSOES[unidade_origem]:
            return valor
        
        return valor * Servidor.CONVERSOES[unidade_origem][unidade_destino]
    
    @property
    def espaco_livre(self):
        """Retorna o espaço livre em disco."""
        return self.espaco_total - self.espaco_usado
    
    @property
    def porcentagem_livre(self):
        """Retorna a porcentagem de espaço livre."""
        if self.espaco_total == 0:
            return 0
        return round((self.espaco_livre / self.espaco_total) * 100, 2)
    
    @property
    def porcentagem_usado(self):
        """Retorna a porcentagem de espaço usado."""
        if self.espaco_total == 0:
            return 0
        return round((self.espaco_usado / self.espaco_total) * 100, 2)
    
    def converter_para_unidade(self, valor, unidade_destino):
        """Converte um valor da unidade do servidor para outra unidade (MB, GB, TB)."""
        return Servidor.converter_unidade(valor, self.unidade, unidade_destino)
    
    def espaco_total_em(self, unidade_destino):
        """Retorna o espaço total convertido para a unidade especificada."""
        return self.converter_para_unidade(self.espaco_total, unidade_destino)
    
    def espaco_usado_em(self, unidade_destino):
        """Retorna o espaço usado convertido para a unidade especificada."""
        return self.converter_para_unidade(self.espaco_usado, unidade_destino)
    
    def espaco_livre_em(self, unidade_destino):
        """Retorna o espaço livre convertido para a unidade especificada."""
        return self.converter_para_unidade(self.espaco_livre, unidade_destino)
    
    def __repr__(self):
        return f'<Servidor {self.id}: {self.nome}>'