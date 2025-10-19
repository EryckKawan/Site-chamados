"""
Script para criar a tabela de Armazenamento de Servidores
Execute este script para inicializar a tabela no banco de dados
"""
import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chamados_ti.db')

def create_storage_table():
    """Cria a tabela de servidores de armazenamento"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela já existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='servidores_storage'")
        if cursor.fetchone():
            print("ℹ️  Tabela 'servidores_storage' já existe.")
            conn.close()
            return True
        
        print("📋 Criando tabela 'servidores_storage'...")
        
        # Criar tabela
        cursor.execute('''
            CREATE TABLE servidores_storage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                capacidade_valor REAL NOT NULL,
                capacidade_unidade TEXT NOT NULL DEFAULT 'GB',
                usado_valor REAL NOT NULL,
                usado_unidade TEXT NOT NULL DEFAULT 'GB',
                observacoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("✅ Tabela 'servidores_storage' criada com sucesso!")
        
        # Inserir dados de exemplo
        print("\n📝 Inserindo dados de exemplo...")
        
        dados_exemplo = [
            ('SRV01 - Principal', 1, 'TB', 400, 'GB', 'Servidor principal de produção'),
            ('SRV02 - Backup', 2, 'TB', 1.5, 'TB', 'Servidor de backup'),
            ('SRV03 - Desenvolvimento', 500, 'GB', 350, 'GB', 'Ambiente de desenvolvimento'),
        ]
        
        cursor.executemany('''
            INSERT INTO servidores_storage 
            (nome, capacidade_valor, capacidade_unidade, usado_valor, usado_unidade, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', dados_exemplo)
        
        conn.commit()
        print(f"✅ {len(dados_exemplo)} servidores de exemplo inseridos!")
        
        # Mostrar estrutura da tabela
        cursor.execute("PRAGMA table_info(servidores_storage)")
        columns = cursor.fetchall()
        print("\n📊 Estrutura da tabela 'servidores_storage':")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Mostrar dados inseridos
        cursor.execute("SELECT * FROM servidores_storage")
        servidores = cursor.fetchall()
        print(f"\n📦 Total de servidores cadastrados: {len(servidores)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("CRIAÇÃO DA TABELA DE ARMAZENAMENTO DE SERVIDORES")
    print("=" * 60)
    create_storage_table()
    print("=" * 60)

