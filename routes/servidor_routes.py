from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import sqlite3
from functools import wraps
from models.servidor import Servidor

# Criando o Blueprint
servidor_bp = Blueprint('servidor', __name__, url_prefix='/servidores')

# Função para obter conexão com o banco de dados
def get_db_connection():
    conn = sqlite3.connect('chamados_ti.db')
    conn.row_factory = sqlite3.Row
    return conn

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator para verificar se o usuário é admin ou técnico
def tech_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] not in ['admin', 'tech']:
            flash('Acesso negado! Apenas técnicos e administradores podem acessar esta página.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Função para converter Row em objeto Servidor
def row_to_servidor(row):
    """Converte um sqlite3.Row em uma instância de Servidor."""
    if not row:
        return None
    
    return Servidor(
        id=row['id'],
        nome=row['nome'],
        ip=row['ip'],
        localizacao=row['localizacao'],
        espaco_total=row['espaco_total'],
        espaco_usado=row['espaco_usado'],
        unidade=row['unidade'],
        observacoes=row['observacoes'],
        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
    )

# Rota para listar todos os servidores
@servidor_bp.route('/')
@login_required
def listar():
    conn = get_db_connection()
    
    # Buscar todos os servidores
    rows = conn.execute('''
        SELECT * FROM servidores
        ORDER BY nome
    ''').fetchall()
    
    # Converter Row objects para objetos Servidor
    servidores = [row_to_servidor(row) for row in rows]
    
    conn.close()
    
    return render_template('servidores.html', servidores=servidores)

# Rota para visualizar detalhes de um servidor
@servidor_bp.route('/<int:id>')
@login_required
def visualizar(id):
    conn = get_db_connection()
    
    # Buscar o servidor pelo ID
    row = conn.execute('SELECT * FROM servidores WHERE id = ?', (id,)).fetchone()
    
    if not row:
        flash('Servidor não encontrado!', 'danger')
        return redirect(url_for('servidor.listar'))
    
    # Converter Row object para objeto Servidor
    servidor = row_to_servidor(row)
    
    conn.close()
    
    return render_template('servidor_detalhes.html', servidor=servidor)

# Rota para o formulário de adição de servidor
@servidor_bp.route('/novo')
@login_required
@tech_required
def novo():
    return render_template('servidor_form.html', servidor=None)

# Rota para o formulário de edição de servidor
@servidor_bp.route('/editar/<int:id>')
@login_required
@tech_required
def editar(id):
    conn = get_db_connection()
    
    # Buscar o servidor pelo ID
    row = conn.execute('SELECT * FROM servidores WHERE id = ?', (id,)).fetchone()
    
    if not row:
        flash('Servidor não encontrado!', 'danger')
        return redirect(url_for('servidor.listar'))
    
    # Converter Row object para objeto Servidor
    servidor = row_to_servidor(row)
    
    conn.close()
    
    return render_template('servidor_form.html', servidor=servidor)

# Rota para salvar um servidor (novo ou editado)
@servidor_bp.route('/salvar', methods=['POST'])
@login_required
@tech_required
def salvar():
    # Obter dados do formulário
    id = request.form.get('id')
    nome = request.form.get('nome')
    ip = request.form.get('ip')
    localizacao = request.form.get('localizacao')
    espaco_total = float(request.form.get('espaco_total', 0))
    espaco_usado = float(request.form.get('espaco_usado', 0))
    unidade = request.form.get('unidade', 'GB')
    observacoes = request.form.get('observacoes')
    
    conn = get_db_connection()
    
    # Verificar se é uma edição ou adição
    if id:
        # Atualizar servidor existente
        conn.execute('''
            UPDATE servidores
            SET nome = ?, ip = ?, localizacao = ?, espaco_total = ?, 
                espaco_usado = ?, unidade = ?, observacoes = ?, updated_at = ?
            WHERE id = ?
        ''', (nome, ip, localizacao, espaco_total, espaco_usado, unidade, 
              observacoes, datetime.now(), id))
        
        flash('Servidor atualizado com sucesso!', 'success')
    else:
        # Adicionar novo servidor
        conn.execute('''
            INSERT INTO servidores 
            (nome, ip, localizacao, espaco_total, espaco_usado, unidade, 
             observacoes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, ip, localizacao, espaco_total, espaco_usado, unidade,
              observacoes, datetime.now(), datetime.now()))
        
        flash('Servidor adicionado com sucesso!', 'success')
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('servidor.listar'))

# Rota para excluir um servidor
@servidor_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
@tech_required
def excluir(id):
    conn = get_db_connection()
    
    # Excluir o servidor
    conn.execute('DELETE FROM servidores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Servidor excluído com sucesso!', 'success')
    return redirect(url_for('servidor.listar'))