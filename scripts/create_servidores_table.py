import sqlite3
import os

def get_db_connection():
    conn = sqlite3.connect('../chamados_ti.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_servidores_table():
    """Cria a tabela de servidores no banco de dados."""
    conn = get_db_connection()
    
    # Verificar se a tabela já existe
    table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='servidores'").fetchone()
    
    if not table_exists:
        print("Criando tabela 'servidores'...")
        conn.execute('''
            CREATE TABLE servidores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                ip TEXT,
                localizacao TEXT,
                espaco_total REAL NOT NULL DEFAULT 0,
                espaco_usado REAL NOT NULL DEFAULT 0,
                unidade TEXT NOT NULL DEFAULT 'GB',
                observacoes TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Tabela 'servidores' criada com sucesso!")
    else:
        print("A tabela 'servidores' já existe.")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Mudar para o diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    create_servidores_table()
    print("Processo concluído!")