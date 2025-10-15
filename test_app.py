from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# Configuração do banco de dados
DATABASE = 'chamados_ti.db'

def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Tabela de chamados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            prioridade TEXT NOT NULL DEFAULT 'media',
            status TEXT NOT NULL DEFAULT 'aberto',
            categoria TEXT NOT NULL,
            criado_por INTEGER NOT NULL,
            atribuido_para INTEGER,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_resolucao TIMESTAMP,
            solucao TEXT,
            equipamento_id INTEGER,
            FOREIGN KEY (criado_por) REFERENCES users (id),
            FOREIGN KEY (atribuido_para) REFERENCES users (id)
        )
    ''')
    
    # Tabela de infraestrutura
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS infraestrutura (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            marca TEXT,
            modelo TEXT,
            numero_serie TEXT,
            localizacao TEXT NOT NULL,
            responsavel TEXT,
            status TEXT NOT NULL DEFAULT 'ativo',
            data_aquisicao DATE,
            data_ultima_manutencao DATE,
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar usuário admin se não existir
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
    ''', ('admin', 'ti@exponencialconsultoria.com.br', admin_password, 'admin'))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obtém conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorator para rotas que requerem login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def is_admin():
    """Verifica se usuário atual é admin"""
    if 'user_id' not in session:
        return False
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return user and user['role'] == 'admin'

def is_tech():
    """Verifica se usuário atual é técnico ou admin"""
    if 'user_id' not in session:
        return False
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return user and user['role'] in ['admin', 'tech']

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND is_active = 1', 
            (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    
    # Estatísticas básicas
    total_chamados = conn.execute('SELECT COUNT(*) FROM chamados').fetchone()[0]
    chamados_abertos = conn.execute("SELECT COUNT(*) FROM chamados WHERE status = 'aberto'").fetchone()[0]
    chamados_em_andamento = conn.execute("SELECT COUNT(*) FROM chamados WHERE status = 'em_andamento'").fetchone()[0]
    chamados_resolvidos = conn.execute("SELECT COUNT(*) FROM chamados WHERE status = 'resolvido'").fetchone()[0]
    
    # Chamados recentes
    if is_tech():
        chamados_recentes = conn.execute('''
            SELECT c.*, u.username as criador_nome
            FROM chamados c
            JOIN users u ON c.criado_por = u.id
            ORDER BY c.data_criacao DESC
            LIMIT 5
        ''').fetchall()
    else:
        chamados_recentes = conn.execute('''
            SELECT c.*, u.username as criador_nome
            FROM chamados c
            JOIN users u ON c.criado_por = u.id
            WHERE c.criado_por = ?
            ORDER BY c.data_criacao DESC
            LIMIT 5
        ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                         total_chamados=total_chamados,
                         chamados_abertos=chamados_abertos,
                         chamados_em_andamento=chamados_em_andamento,
                         chamados_resolvidos=chamados_resolvidos,
                         chamados_recentes=chamados_recentes)

@app.route('/chamados')
@login_required
def chamados():
    conn = get_db_connection()
    
    if is_tech():
        chamados = conn.execute('''
            SELECT c.*, u.username as criador_nome, u2.username as tecnico_nome
            FROM chamados c
            JOIN users u ON c.criado_por = u.id
            LEFT JOIN users u2 ON c.atribuido_para = u2.id
            ORDER BY c.data_criacao DESC
        ''').fetchall()
    else:
        chamados = conn.execute('''
            SELECT c.*, u.username as criador_nome, u2.username as tecnico_nome
            FROM chamados c
            JOIN users u ON c.criado_por = u.id
            LEFT JOIN users u2 ON c.atribuido_para = u2.id
            WHERE c.criado_por = ?
            ORDER BY c.data_criacao DESC
        ''', (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('chamados.html', chamados=chamados)

@app.route('/chamados/novo', methods=['GET', 'POST'])
@login_required
def novo_chamado():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO chamados (titulo, descricao, prioridade, categoria, criado_por)
            VALUES (?, ?, ?, ?, ?)
        ''', (titulo, descricao, prioridade, categoria, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Chamado criado com sucesso!', 'success')
        return redirect(url_for('chamados'))
    
    return render_template('chamado_form.html')

@app.route('/infraestrutura')
@login_required
def infraestrutura():
    if not is_tech():
        flash('Acesso negado!', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    equipamentos = conn.execute('SELECT * FROM infraestrutura ORDER BY nome').fetchall()
    conn.close()
    
    return render_template('infraestrutura.html', equipamentos=equipamentos)

@app.route('/infraestrutura/novo', methods=['GET', 'POST'])
@login_required
def novo_equipamento():
    if not is_tech():
        flash('Acesso negado!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        marca = request.form.get('marca', '')
        modelo = request.form.get('modelo', '')
        localizacao = request.form['localizacao']
        responsavel = request.form.get('responsavel', '')
        status = request.form['status']
        observacoes = request.form.get('observacoes', '')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO infraestrutura (nome, tipo, marca, modelo, localizacao, responsavel, status, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, tipo, marca, modelo, localizacao, responsavel, status, observacoes))
        conn.commit()
        conn.close()
        
        flash('Equipamento cadastrado com sucesso!', 'success')
        return redirect(url_for('infraestrutura'))
    
    return render_template('infra_form.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Endpoint para futura integração com OpenAI API"""
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Respostas simuladas para mensagens comuns
    responses = {
        'resetar impressora': 'Para resetar a impressora: 1) Desligue a impressora, 2) Aguarde 30 segundos, 3) Ligue novamente, 4) Teste imprimindo uma página de teste.',
        'senha': 'Para redefinir senha, acesse o portal do usuário ou entre em contato com o suporte técnico.',
        'email': 'Problemas com email podem ser resolvidos verificando as configurações do Outlook ou acessando o webmail.',
        'internet': 'Para problemas de internet, verifique se o cabo de rede está conectado e tente reiniciar o roteador.',
        'computador lento': 'Para melhorar a performance: 1) Reinicie o computador, 2) Feche programas desnecessários, 3) Execute limpeza de disco.',
    }
    
    for keyword, response in responses.items():
        if keyword in message:
            return jsonify({'response': response})
    
    return jsonify({'response': 'Não encontrei uma resposta automática para sua pergunta. Um técnico entrará em contato em breve.'})

if __name__ == '__main__':
    init_db()
    print("🚀 Sistema de Chamados TI iniciado!")
    print("📱 Acesse: http://127.0.0.1:5000")
    print("🔑 Login: admin / admin123")
    app.run(debug=True, host='127.0.0.1', port=5000)
