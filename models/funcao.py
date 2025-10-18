from datetime import datetime

class Funcao:
    """Modelo para representar funções/cargos no sistema."""
    
    def __init__(self, id=None, nome=None, nivel_acesso=None, descricao=None, 
                 created_at=None, updated_at=None):
        self.id = id
        self.nome = nome  # Ex: Diretor, Monitor, Supervisor, Auxiliar Adm
        self.nivel_acesso = nivel_acesso  # Nível numérico de acesso (1-5, onde 5 é o mais alto)
        self.descricao = descricao
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_db_row(cls, row):
        """Cria uma instância de Funcao a partir de uma linha do banco de dados."""
        if not row:
            return None
        
        return cls(
            id=row['id'],
            nome=row['nome'],
            nivel_acesso=row['nivel_acesso'],
            descricao=row['descricao'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def to_dict(self):
        """Converte a instância para um dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'nivel_acesso': self.nivel_acesso,
            'descricao': self.descricao,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }