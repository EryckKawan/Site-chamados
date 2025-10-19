"""
Rotas para Armazenamento de Servidores
CRUD completo com cálculos automáticos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

# Criar blueprint
servidor_storage_bp = Blueprint('servidor_storage', __name__, url_prefix='/storage')

# Configuração do banco de dados
DATABASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chamados_ti.db')

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
            from flask import redirect, url_for
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def can_access_storage():
    """Verifica se usuário pode acessar armazenamento"""
    if 'user_id' not in session:
        return False
    role = session.get('role')
    return role in ['admin', 'diretor', 'supervisor', 'tech']


@servidor_storage_bp.route('/')
@login_required
def listar():
    """Lista todos os servidores de armazenamento"""
    if not can_access_storage():
        flash('Acesso negado! Você não tem permissão para acessar o armazenamento de servidores.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    servidores_raw = conn.execute('''
        SELECT * FROM servidores_storage 
        ORDER BY nome
    ''').fetchall()
    conn.close()
    
    # Processar dados e adicionar cálculos
    servidores = []
    for srv in servidores_raw:
        # Conversão para GB
        capacidade_gb = float(srv['capacidade_valor']) * 1024 if srv['capacidade_unidade'] == 'TB' else float(srv['capacidade_valor'])
        usado_gb = float(srv['usado_valor']) * 1024 if srv['usado_unidade'] == 'TB' else float(srv['usado_valor'])
        
        # Cálculos
        livre_gb = capacidade_gb - usado_gb
        percentual_uso = (usado_gb / capacidade_gb * 100) if capacidade_gb > 0 else 0
        percentual_livre = 100 - percentual_uso
        
        # Status de cor
        if percentual_uso < 70:
            status_cor = 'success'
        elif percentual_uso < 85:
            status_cor = 'warning'
        else:
            status_cor = 'danger'
        
        servidores.append({
            'id': srv['id'],
            'nome': srv['nome'],
            'capacidade_valor': srv['capacidade_valor'],
            'capacidade_unidade': srv['capacidade_unidade'],
            'usado_valor': srv['usado_valor'],
            'usado_unidade': srv['usado_unidade'],
            'capacidade_gb': round(capacidade_gb, 2),
            'usado_gb': round(usado_gb, 2),
            'livre_gb': round(livre_gb, 2),
            'percentual_uso': round(percentual_uso, 2),
            'percentual_livre': round(percentual_livre, 2),
            'status_cor': status_cor,
            'observacoes': srv['observacoes']
        })
    
    return render_template('servidores_storage.html', servidores=servidores)


@servidor_storage_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Adiciona um novo servidor de armazenamento"""
    if not can_access_storage():
        flash('Acesso negado! Você não tem permissão para acessar o armazenamento de servidores.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        capacidade_valor = float(request.form['capacidade_valor'])
        capacidade_unidade = request.form['capacidade_unidade']
        usado_valor = float(request.form['usado_valor'])
        usado_unidade = request.form['usado_unidade']
        observacoes = request.form.get('observacoes', '')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO servidores_storage 
            (nome, capacidade_valor, capacidade_unidade, usado_valor, usado_unidade, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, capacidade_valor, capacidade_unidade, usado_valor, usado_unidade, observacoes))
        conn.commit()
        conn.close()
        
        flash(f'Servidor "{nome}" adicionado com sucesso!', 'success')
        return redirect(url_for('servidor_storage.listar'))
    
    return render_template('servidor_storage_form.html', action='novo')


@servidor_storage_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um servidor de armazenamento existente"""
    if not can_access_storage():
        flash('Acesso negado! Você não tem permissão para acessar o armazenamento de servidores.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    servidor = conn.execute('SELECT * FROM servidores_storage WHERE id = ?', (id,)).fetchone()
    
    if not servidor:
        flash('Servidor não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('servidor_storage.listar'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        capacidade_valor = float(request.form['capacidade_valor'])
        capacidade_unidade = request.form['capacidade_unidade']
        usado_valor = float(request.form['usado_valor'])
        usado_unidade = request.form['usado_unidade']
        observacoes = request.form.get('observacoes', '')
        
        conn.execute('''
            UPDATE servidores_storage 
            SET nome = ?, capacidade_valor = ?, capacidade_unidade = ?, 
                usado_valor = ?, usado_unidade = ?, observacoes = ?
            WHERE id = ?
        ''', (nome, capacidade_valor, capacidade_unidade, usado_valor, usado_unidade, observacoes, id))
        conn.commit()
        conn.close()
        
        flash(f'Servidor "{nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('servidor_storage.listar'))
    
    conn.close()
    return render_template('servidor_storage_form.html', servidor=servidor, action='editar')


@servidor_storage_bp.route('/<int:id>/deletar', methods=['POST'])
@login_required
def deletar(id):
    """Deleta um servidor de armazenamento"""
    if session.get('role') != 'admin':
        flash('Acesso negado! Apenas administradores podem deletar.', 'danger')
        return redirect(url_for('servidor_storage.listar'))
    
    conn = get_db_connection()
    servidor = conn.execute('SELECT nome FROM servidores_storage WHERE id = ?', (id,)).fetchone()
    
    if not servidor:
        flash('Servidor não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('servidor_storage.listar'))
    
    conn.execute('DELETE FROM servidores_storage WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash(f'Servidor "{servidor["nome"]}" deletado com sucesso!', 'success')
    return redirect(url_for('servidor_storage.listar'))

