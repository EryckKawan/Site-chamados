"""
Módulo de configuração de banco de dados
Suporta SQLite (desenvolvimento) e PostgreSQL (produção)
"""
import os
import sqlite3
from urllib.parse import urlparse

# Detectar ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    # PostgreSQL
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    # Corrigir URL se necessário (Render usa postgres:// mas psycopg2 precisa postgresql://)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    print("🐘 Usando PostgreSQL em produção")
    
    def get_db_connection():
        """Conexão PostgreSQL"""
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        return conn
    
else:
    # SQLite (desenvolvimento)
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chamados_ti.db')
    print(f"📁 Usando SQLite: {DATABASE}")
    
    def get_db_connection():
        """Conexão SQLite"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        # PostgreSQL - Sintaxe específica
        print("🔧 Criando tabelas no PostgreSQL...")
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                funcao_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de funções
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funcoes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL,
                descricao TEXT,
                permissoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de chamados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chamados (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                descricao TEXT,
                status VARCHAR(20) DEFAULT 'aberto',
                prioridade VARCHAR(20) DEFAULT 'media',
                usuario_id INTEGER REFERENCES users(id),
                atribuido_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de mensagens do chat
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_mensagens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                username VARCHAR(100),
                mensagem TEXT NOT NULL,
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                lida BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Tabela de permissões de usuário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                permission_key VARCHAR(100) NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                UNIQUE(user_id, permission_key)
            )
        ''')
        
        # Tabela de servidores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servidores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL,
                tipo VARCHAR(50),
                ip_address VARCHAR(45),
                status VARCHAR(20) DEFAULT 'ativo',
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de armazenamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS armazenamentos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL,
                tipo VARCHAR(50),
                capacidade_total BIGINT,
                capacidade_usada BIGINT,
                status VARCHAR(20) DEFAULT 'ativo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de backup de storage de servidores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servidores_storage_backup (
                id SERIAL PRIMARY KEY,
                servidor_id INTEGER REFERENCES servidores(id),
                nome_storage VARCHAR(255),
                caminho_storage VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de nomes de roles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_names (
                id SERIAL PRIMARY KEY,
                role_key VARCHAR(50) UNIQUE NOT NULL,
                display_name VARCHAR(100) NOT NULL
            )
        ''')
        
    else:
        # SQLite - Sintaxe específica
        print("🔧 Criando tabelas no SQLite...")
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                funcao_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de funções
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funcoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT,
                permissoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de chamados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                status TEXT DEFAULT 'aberto',
                prioridade TEXT DEFAULT 'media',
                usuario_id INTEGER,
                atribuido_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES users (id),
                FOREIGN KEY (atribuido_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de mensagens do chat
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                mensagem TEXT NOT NULL,
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                lida BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de permissões de usuário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                permission_key TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                UNIQUE(user_id, permission_key),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabela de servidores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servidores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                tipo TEXT,
                ip_address TEXT,
                status TEXT DEFAULT 'ativo',
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de armazenamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS armazenamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                tipo TEXT,
                capacidade_total INTEGER,
                capacidade_usada INTEGER,
                status TEXT DEFAULT 'ativo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de backup de storage de servidores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servidores_storage_backup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servidor_id INTEGER,
                nome_storage TEXT,
                caminho_storage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (servidor_id) REFERENCES servidores (id)
            )
        ''')
        
        # Tabela de nomes de roles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_key TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL
            )
        ''')
    
    # Inserir dados padrão (funciona em ambos)
    cursor.execute("SELECT COUNT(*) as count FROM role_names")
    if USE_POSTGRES:
        count = cursor.fetchone()['count']
    else:
        count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("INSERT INTO role_names (role_key, display_name) VALUES ('admin', 'Administrador')")
        cursor.execute("INSERT INTO role_names (role_key, display_name) VALUES ('user', 'Usuário')")
        cursor.execute("INSERT INTO role_names (role_key, display_name) VALUES ('suporte', 'Suporte TI')")
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")


if __name__ == '__main__':
    # Permitir executar database.py diretamente para inicializar
    init_db()

