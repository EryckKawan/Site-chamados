from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from functools import wraps
from models.funcao import Funcao
import datetime

funcao_bp = Blueprint('funcao', __name__, url_prefix='/funcoes')

def get_db_connection():
    conn = sqlite3.connect('chamados_ti.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        
        # Verificar se o usuário é administrador ou tem função de Diretor
        if not (user['role'] == 'admin' or user['funcao_id'] == 1):  # 1 = Diretor (nível mais alto)
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

@funcao_bp.route('/')
@login_required
@admin_required
def listar_funcoes():
    """Lista todas as funções cadastradas."""
    conn = get_db_connection()
    funcoes_rows = conn.execute('SELECT * FROM funcoes ORDER BY nivel_acesso DESC').fetchall()
    conn.close()
    
    funcoes = [Funcao.from_db_row(row) for row in funcoes_rows]
    
    return render_template('funcoes.html', funcoes=funcoes)

@funcao_bp.route('/adicionar', methods=['GET', 'POST'])
@login_required
@admin_required
def adicionar_funcao():
    """Adiciona uma nova função."""
    if request.method == 'POST':
        nome = request.form.get('nome')
        nivel_acesso = request.form.get('nivel_acesso', type=int)
        descricao = request.form.get('descricao')
        
        if not nome:
            flash('O nome da função é obrigatório.', 'danger')
            return redirect(url_for('funcao.adicionar_funcao'))
        
        if not nivel_acesso or nivel_acesso < 1 or nivel_acesso > 5:
            flash('O nível de acesso deve ser um número entre 1 e 5.', 'danger')
            return redirect(url_for('funcao.adicionar_funcao'))
        
        conn = get_db_connection()
        
        # Verificar se já existe uma função com o mesmo nome
        funcao_existente = conn.execute('SELECT * FROM funcoes WHERE nome = ?', (nome,)).fetchone()
        if funcao_existente:
            conn.close()
            flash(f'Já existe uma função com o nome "{nome}".', 'danger')
            return redirect(url_for('funcao.adicionar_funcao'))
        
        conn.execute('''
            INSERT INTO funcoes (nome, nivel_acesso, descricao)
            VALUES (?, ?, ?)
        ''', (nome, nivel_acesso, descricao))
        
        conn.commit()
        conn.close()
        
        flash(f'Função "{nome}" adicionada com sucesso!', 'success')
        return redirect(url_for('funcao.listar_funcoes'))
    
    return render_template('funcao_form.html', funcao=None)

@funcao_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_funcao(id):
    """Edita uma função existente."""
    conn = get_db_connection()
    funcao_row = conn.execute('SELECT * FROM funcoes WHERE id = ?', (id,)).fetchone()
    
    if not funcao_row:
        conn.close()
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcao.listar_funcoes'))
    
    funcao = Funcao.from_db_row(funcao_row)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        nivel_acesso = request.form.get('nivel_acesso', type=int)
        descricao = request.form.get('descricao')
        
        if not nome:
            flash('O nome da função é obrigatório.', 'danger')
            return redirect(url_for('funcao.editar_funcao', id=id))
        
        if not nivel_acesso or nivel_acesso < 1 or nivel_acesso > 5:
            flash('O nível de acesso deve ser um número entre 1 e 5.', 'danger')
            return redirect(url_for('funcao.editar_funcao', id=id))
        
        # Verificar se já existe outra função com o mesmo nome
        funcao_existente = conn.execute('SELECT * FROM funcoes WHERE nome = ? AND id != ?', 
                                       (nome, id)).fetchone()
        if funcao_existente:
            conn.close()
            flash(f'Já existe outra função com o nome "{nome}".', 'danger')
            return redirect(url_for('funcao.editar_funcao', id=id))
        
        conn.execute('''
            UPDATE funcoes
            SET nome = ?, nivel_acesso = ?, descricao = ?, updated_at = ?
            WHERE id = ?
        ''', (nome, nivel_acesso, descricao, datetime.datetime.now(), id))
        
        conn.commit()
        conn.close()
        
        flash(f'Função "{nome}" atualizada com sucesso!', 'success')
        return redirect(url_for('funcao.listar_funcoes'))
    
    conn.close()
    return render_template('funcao_form.html', funcao=funcao)

@funcao_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
@admin_required
def excluir_funcao(id):
    """Exclui uma função."""
    conn = get_db_connection()
    
    # Verificar se a função existe
    funcao = conn.execute('SELECT * FROM funcoes WHERE id = ?', (id,)).fetchone()
    if not funcao:
        conn.close()
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcao.listar_funcoes'))
    
    # Verificar se existem usuários usando esta função
    usuarios = conn.execute('SELECT COUNT(*) as count FROM users WHERE funcao_id = ?', (id,)).fetchone()
    if usuarios['count'] > 0:
        conn.close()
        flash(f'Não é possível excluir a função "{funcao["nome"]}" pois existem usuários associados a ela.', 'danger')
        return redirect(url_for('funcao.listar_funcoes'))
    
    # Excluir a função
    conn.execute('DELETE FROM funcoes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash(f'Função "{funcao["nome"]}" excluída com sucesso!', 'success')
    return redirect(url_for('funcao.listar_funcoes'))