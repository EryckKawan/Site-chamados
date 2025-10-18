import sqlite3
import os

def get_db_connection():
    conn = sqlite3.connect('../chamados_ti.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_funcoes_table():
    """Cria a tabela de funções/cargos no banco de dados."""
    conn = get_db_connection()
    
    # Verificar se a tabela já existe
    table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='funcoes'").fetchone()
    
    if not table_exists:
        print("Criando tabela 'funcoes'...")
        conn.execute('''
            CREATE TABLE funcoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                nivel_acesso INTEGER NOT NULL DEFAULT 1,
                descricao TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inserir funções padrão
        funcoes_padrao = [
            ('Diretor', 5, 'Acesso total ao sistema'),
            ('Supervisor', 4, 'Acesso a gerenciamento de usuários e configurações'),
            ('Monitor', 3, 'Acesso a relatórios e monitoramento'),
            ('Auxiliar Administrativo', 2, 'Acesso básico administrativo'),
            ('Usuário', 1, 'Acesso básico ao sistema')
        ]
        
        for funcao in funcoes_padrao:
            conn.execute('''
                INSERT INTO funcoes (nome, nivel_acesso, descricao)
                VALUES (?, ?, ?)
            ''', funcao)
            
        print("Tabela 'funcoes' criada com sucesso!")
        print("Funções padrão inseridas: Diretor, Supervisor, Monitor, Auxiliar Administrativo, Usuário")
    else:
        print("A tabela 'funcoes' já existe.")
    
    # Adicionar coluna de função na tabela de usuários se não existir
    user_table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    
    if user_table_exists:
        # Verificar se a coluna funcao_id já existe na tabela users
        columns = conn.execute("PRAGMA table_info(users)").fetchall()
        funcao_id_exists = any(column[1] == 'funcao_id' for column in columns)
        
        if not funcao_id_exists:
            print("Adicionando coluna 'funcao_id' à tabela 'users'...")
            conn.execute('''
                ALTER TABLE users
                ADD COLUMN funcao_id INTEGER DEFAULT 1
                REFERENCES funcoes(id)
            ''')
            print("Coluna 'funcao_id' adicionada com sucesso!")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Mudar para o diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    create_funcoes_table()
    print("Processo concluído!")