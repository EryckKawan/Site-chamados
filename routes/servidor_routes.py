from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime

servidor_bp = Blueprint('servidor', __name__, url_prefix='/storage')

DATABASE = 'chamados_ti.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            from flask import redirect, url_for
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def can_access_storage():
    if 'user_id' not in session:
        return False
    role = session.get('role')
    return role in ['admin', 'diretor', 'supervisor', 'tech']


@servidor_bp.route('/')
@login_required
def listar_servidores():
    """Lista todos os servidores com seus armazenamentos"""
    if not can_access_storage():
        flash('Acesso negado! Você não tem permissão para acessar o armazenamento de servidores.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    
    # Buscar servidores
    servidores_raw = conn.execute('''
        SELECT * FROM servidores
        ORDER BY nome
    ''').fetchall()
    
    servidores = []
    for servidor_row in servidores_raw:
        servidor = dict(servidor_row)
        
        # Buscar armazenamentos do servidor
        armazenamentos_raw = conn.execute('''
            SELECT * FROM armazenamentos
            WHERE servidor_id = ?
            ORDER BY nome
        ''', (servidor['id'],)).fetchall()
        
        armazenamentos = []
        for arm_row in armazenamentos_raw:
            armazenamento = dict(arm_row)
            
            # Adicionar propriedades calculadas
            class MockArmazenamento:
                def __init__(self, data):
                    self.__dict__.update(data)
                    self.capacidade_gb = round(self._to_gb(self.capacidade_valor, self.capacidade_unidade), 2)
                    self.usado_gb = round(self._to_gb(self.usado_valor, self.usado_unidade), 2)
                    self.livre_gb = round(self.capacidade_gb - self.usado_gb, 2)
                    self.percentual_uso = round((self.usado_gb / self.capacidade_gb) * 100, 2) if self.capacidade_gb > 0 else 0.0
                    self.percentual_livre = round(100 - self.percentual_uso, 2)
                    self.status_cor = self._get_status_cor(self.percentual_uso)

                def _to_gb(self, valor, unidade):
                    if unidade.upper() == 'TB':
                        return valor * 1024
                    elif unidade.upper() == 'MB':
                        return valor / 1024
                    return valor

                def _get_status_cor(self, percentual_uso):
                    if percentual_uso < 70:
                        return 'success'
                    elif percentual_uso < 85:
                        return 'warning'
                    return 'danger'
            
            armazenamentos.append(MockArmazenamento(armazenamento))
        
        # Adicionar propriedades calculadas do servidor
        class MockServidor:
            def __init__(self, data, armazenamentos):
                self.__dict__.update(data)
                self.armazenamentos = armazenamentos
                self.total_armazenamentos = len(armazenamentos)
                
                # Calcular totais
                self.capacidade_total_gb = sum(arm.capacidade_gb for arm in armazenamentos)
                self.usado_total_gb = sum(arm.usado_gb for arm in armazenamentos)
                self.livre_total_gb = round(self.capacidade_total_gb - self.usado_total_gb, 2)
                self.percentual_uso_total = round((self.usado_total_gb / self.capacidade_total_gb) * 100, 2) if self.capacidade_total_gb > 0 else 0.0
                self.status_cor_total = self._get_status_cor(self.percentual_uso_total)
            
            def _get_status_cor(self, percentual_uso):
                if percentual_uso < 70:
                    return 'success'
                elif percentual_uso < 85:
                    return 'warning'
                return 'danger'
        
        servidores.append(MockServidor(servidor, armazenamentos))
    
    conn.close()
    return render_template('servidores_lista.html', servidores=servidores)


@servidor_bp.route('/novo-servidor', methods=['GET', 'POST'])
@login_required
def novo_servidor():
    """Adiciona um novo servidor"""
    if not can_access_storage():
        flash('Acesso negado! Você não tem permissão para acessar o armazenamento de servidores.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        ip_endereco = request.form.get('ip_endereco', '')
        sistema_operacional = request.form.get('sistema_operacional', '')
        observacoes = request.form.get('observacoes', '')

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO servidores (nome, descricao, ip_endereco, sistema_operacional, observacoes)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, descricao, ip_endereco, sistema_operacional, observacoes))
        conn.commit()
        conn.close()

        flash('Servidor adicionado com sucesso!', 'success')
        return redirect(url_for('servidor.listar_servidores'))

    return render_template('servidor_form.html', action='novo-servidor')


@servidor_bp.route('/<int:servidor_id>/novo-armazenamento', methods=['GET', 'POST'])
@login_required
def novo_armazenamento(servidor_id):
    """Adiciona um novo armazenamento a um servidor"""
    if not can_access_storage():
        flash('Acesso negado! Você não tem permissão para acessar o armazenamento de servidores.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    servidor = conn.execute('SELECT * FROM servidores WHERE id = ?', (servidor_id,)).fetchone()

    if not servidor:
        flash('Servidor não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('servidor.listar_servidores'))

    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        capacidade_valor = float(request.form['capacidade_valor'])
        capacidade_unidade = request.form['capacidade_unidade']
        usado_valor = float(request.form['usado_valor'])
        usado_unidade = request.form['usado_unidade']
        observacoes = request.form.get('observacoes', '')

        conn.execute('''
            INSERT INTO armazenamentos (servidor_id, nome, tipo, capacidade_valor, capacidade_unidade, usado_valor, usado_unidade, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (servidor_id, nome, tipo, capacidade_valor, capacidade_unidade, usado_valor, usado_unidade, observacoes))
        conn.commit()
        conn.close()

        flash('Armazenamento adicionado com sucesso!', 'success')
        return redirect(url_for('servidor.listar_servidores'))

    conn.close()
    return render_template('armazenamento_form.html', servidor=servidor, action='novo-armazenamento')


@servidor_bp.route('/armazenamento/<int:armazenamento_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_armazenamento(armazenamento_id):
    """Edita um armazenamento existente"""
    if not can_access_storage():
        flash('Acesso negado! Você não tem permissão para acessar o armazenamento de servidores.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    armazenamento = conn.execute('''
        SELECT a.*, s.nome as servidor_nome 
        FROM armazenamentos a 
        JOIN servidores s ON a.servidor_id = s.id 
        WHERE a.id = ?
    ''', (armazenamento_id,)).fetchone()

    if not armazenamento:
        flash('Armazenamento não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('servidor.listar_servidores'))

    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        capacidade_valor = float(request.form['capacidade_valor'])
        capacidade_unidade = request.form['capacidade_unidade']
        usado_valor = float(request.form['usado_valor'])
        usado_unidade = request.form['usado_unidade']
        observacoes = request.form.get('observacoes', '')

        conn.execute('''
            UPDATE armazenamentos
            SET nome = ?, tipo = ?, capacidade_valor = ?, capacidade_unidade = ?,
                usado_valor = ?, usado_unidade = ?, observacoes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (nome, tipo, capacidade_valor, capacidade_unidade,
              usado_valor, usado_unidade, observacoes, armazenamento_id))
        conn.commit()
        conn.close()

        flash('Armazenamento atualizado com sucesso!', 'success')
        return redirect(url_for('servidor.listar_servidores'))

    conn.close()
    return render_template('armazenamento_form.html', armazenamento=armazenamento, action='editar')


@servidor_bp.route('/armazenamento/<int:armazenamento_id>/deletar', methods=['POST'])
@login_required
def deletar_armazenamento(armazenamento_id):
    """Deleta um armazenamento"""
    if session.get('role') != 'admin':
        flash('Acesso negado! Apenas administradores podem deletar.', 'danger')
        return redirect(url_for('servidor.listar_servidores'))

    conn = get_db_connection()
    armazenamento = conn.execute('''
        SELECT a.nome, s.nome as servidor_nome 
        FROM armazenamentos a 
        JOIN servidores s ON a.servidor_id = s.id 
        WHERE a.id = ?
    ''', (armazenamento_id,)).fetchone()

    if not armazenamento:
        flash('Armazenamento não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('servidor.listar_servidores'))

    conn.execute('DELETE FROM armazenamentos WHERE id = ?', (armazenamento_id,))
    conn.commit()
    conn.close()

    flash(f'Armazenamento "{armazenamento["nome"]}" do servidor "{armazenamento["servidor_nome"]}" deletado com sucesso!', 'success')
    return redirect(url_for('servidor.listar_servidores'))


@servidor_bp.route('/servidor/<int:servidor_id>/deletar', methods=['POST'])
@login_required
def deletar_servidor(servidor_id):
    """Deleta um servidor e todos seus armazenamentos"""
    if session.get('role') != 'admin':
        flash('Acesso negado! Apenas administradores podem deletar.', 'danger')
        return redirect(url_for('servidor.listar_servidores'))

    conn = get_db_connection()
    servidor = conn.execute('SELECT nome FROM servidores WHERE id = ?', (servidor_id,)).fetchone()

    if not servidor:
        flash('Servidor não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('servidor.listar_servidores'))

    # Deletar armazenamentos primeiro (cascade)
    conn.execute('DELETE FROM armazenamentos WHERE servidor_id = ?', (servidor_id,))
    # Deletar servidor
    conn.execute('DELETE FROM servidores WHERE id = ?', (servidor_id,))
    conn.commit()
    conn.close()

    flash(f'Servidor "{servidor["nome"]}" e todos seus armazenamentos foram deletados com sucesso!', 'success')
    return redirect(url_for('servidor.listar_servidores'))
