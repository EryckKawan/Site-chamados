#!/usr/bin/env python3
"""
Script de inicialização do Sistema de Chamados TI
"""

import os
import sys
from app import app, get_db_connection
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Cria usuário admin se não existir"""
    conn = get_db_connection()
    
    # Verificar se admin já existe
    admin = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin:
        password_hash = generate_password_hash('admin123')
        conn.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
    ''', ('admin', 'ti@exponencialconsultoria.com.br', password_hash, 'admin'))
        conn.commit()
        print("✅ Usuário admin criado: admin / admin123")
    else:
        print("ℹ️  Usuário admin já existe")
    
    conn.close()

def create_sample_data():
    """Cria dados de exemplo para demonstração"""
    conn = get_db_connection()
    
    # Verificar se já existem dados
    chamados_count = conn.execute('SELECT COUNT(*) FROM chamados').fetchone()[0]
    if chamados_count > 0:
        print("ℹ️  Dados de exemplo já existem")
        conn.close()
        return
    
    # Criar equipamentos de exemplo
    equipamentos = [
        ("PC Administração", "computador", "Dell", "OptiPlex 7090", "Sala 101", "João Silva", "ativo"),
        ("Impressora Central", "impressora", "HP", "LaserJet Pro", "Recepção", "Maria Santos", "ativo"),
        ("Servidor Principal", "servidor", "IBM", "System x3650", "Datacenter", "Carlos Admin", "ativo")
    ]
    
    for equipamento in equipamentos:
        conn.execute('''
            INSERT INTO infraestrutura (nome, tipo, marca, modelo, localizacao, responsavel, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', equipamento)
    
    conn.commit()
    print("✅ Equipamentos de exemplo criados")
    
    # Criar usuário comum para testes
    user_password = generate_password_hash('usuario123')
    conn.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', ('usuario', 'usuario@empresa.com', user_password, 'user'))
    
    # Criar técnico para testes
    tech_password = generate_password_hash('tecnico123')
    conn.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', ('tecnico', 'tecnico@empresa.com', tech_password, 'tech'))
    
    conn.commit()
    print("✅ Usuários de exemplo criados")
    
    # Obter IDs dos usuários
    user_id = conn.execute('SELECT id FROM users WHERE username = ?', ('usuario',)).fetchone()[0]
    tech_id = conn.execute('SELECT id FROM users WHERE username = ?', ('tecnico',)).fetchone()[0]
    
    # Criar chamados de exemplo
    chamados = [
        ("Computador não liga", "O computador da sala 101 não está ligando. Verifiquei a energia e está tudo ok.", "alta", "hardware", user_id, 1),
        ("Impressora com papel preso", "A impressora da recepção está com papel preso e não está imprimindo.", "media", "impressora", user_id, 2),
        ("Email não está funcionando", "Não consigo enviar emails pelo Outlook. Aparece erro de conexão.", "alta", "email", user_id, None)
    ]
    
    for chamado in chamados:
        conn.execute('''
            INSERT INTO chamados (titulo, descricao, prioridade, categoria, criado_por, equipamento_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', chamado)
    
    conn.commit()
    print("✅ Chamados de exemplo criados")
    print("\n🎉 Dados de exemplo criados com sucesso!")
    print("\nUsuários disponíveis:")
    print("- admin / admin123 (Administrador)")
    print("- tecnico / tecnico123 (Técnico)")
    print("- usuario / usuario123 (Usuário comum)")
    
    conn.close()

def main():
    """Função principal"""
    print("🚀 Inicializando Sistema de Chamados TI...")
    
    # Inicializar banco de dados
    from app import init_db
    init_db()
    print("✅ Banco de dados inicializado")
    
    # Criar usuário admin
    create_admin_user()
    
    # Perguntar se quer criar dados de exemplo
    if len(sys.argv) > 1 and sys.argv[1] == '--sample':
        create_sample_data()
    else:
        resposta = input("\nDeseja criar dados de exemplo? (s/n): ").lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            create_sample_data()
    
    print("\n🌐 Iniciando servidor...")
    print("📱 Acesse: http://127.0.0.1:5000")
    print("🔑 Login: admin / admin123")
    print("\nPressione Ctrl+C para parar o servidor")
    
    # Iniciar servidor
    app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()

