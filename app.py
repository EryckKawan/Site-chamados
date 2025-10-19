from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import math
from routes.funcao_routes import funcao_bp
from routes.servidor_routes import servidor_bp

app = Flask(__name__)

# Configurações de segurança e sessão
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-super-segura-2024')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Sessão dura 24 horas
app.config['SESSION_COOKIE_SECURE'] = False  # True apenas em HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Registrando blueprints
app.register_blueprint(funcao_bp)
app.register_blueprint(servidor_bp)

class Pagination:
    """Simple pagination class to mimic Flask-SQLAlchemy pagination"""
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = math.ceil(total / per_page) if per_page > 0 else 0
        self.prev_num = page - 1 if page > 1 else None
        self.next_num = page + 1 if page < self.pages else None
        self.has_prev = self.prev_num is not None
        self.has_next = self.next_num is not None

class MockUser:
    """Mock user object to match template expectations"""
    def __init__(self, username):
        self.username = username

def convert_chamado_row(row):
    """Convert SQLite Row to object with expected attributes"""
    class MockChamado:
        def __init__(self, row):
            # Copy all original fields
            for key in row.keys():
                setattr(self, key, row[key])
            
            # Add expected object attributes
            self.criador = MockUser(row['criador_nome'] if 'criador_nome' in row.keys() else '')
            self.tecnico = MockUser(row['tecnico_nome']) if 'tecnico_nome' in row.keys() and row['tecnico_nome'] else None
        
        @property
        def prioridade_class(self):
            classes = {
                'baixa': 'success',
                'media': 'warning', 
                'alta': 'danger',
                'critica': 'dark'
            }
            return classes.get(self.prioridade, 'secondary')
        
        @property
        def status_class(self):
            classes = {
                'aberto': 'primary',
                'em_andamento': 'warning',
                'resolvido': 'success',
                'fechado': 'secondary'
            }
            return classes.get(self.status, 'secondary')

        @property
        def tempo_aberto(self):
            """Compute a timedelta for how long the chamado has been open.

            Handles datetime objects or common string formats coming from sqlite rows.
            """
            from datetime import datetime

            def _to_dt(value):
                if value is None:
                    return None
                if isinstance(value, datetime):
                    return value
                if isinstance(value, str):
                    # Try common formats
                    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    try:
                        return datetime.fromisoformat(value)
                    except Exception:
                        return None
                return None

            start = _to_dt(getattr(self, 'data_criacao', None))
            end = _to_dt(getattr(self, 'data_resolucao', None))

            if start is None:
                from datetime import timedelta
                return timedelta(0)
            if end:
                return end - start
            from datetime import datetime as _dt
            return _dt.utcnow() - start
    
    return MockChamado(row)

# Custom Jinja2 filter for safe date formatting
@app.template_filter('format_date')
def format_date_filter(value, format='%d/%m/%Y'):
    """Safely format dates, handling None, strings, and datetime objects"""
    if value is None:
        return 'N/A'
    
    # If it's already a datetime object
    if isinstance(value, datetime):
        return value.strftime(format)
    
    # If it's a string, try to parse it
    if isinstance(value, str):
        try:
            # Try parsing as datetime
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return dt.strftime(format)
        except ValueError:
            try:
                # Try parsing as date only
                dt = datetime.strptime(value, '%Y-%m-%d')
                return dt.strftime(format)
            except ValueError:
                # If parsing fails, return the original string
                return value
    
    # For any other type, return as string
    return str(value)

# Custom Jinja2 filter to convert string to datetime
@app.template_filter('to_datetime')
def to_datetime_filter(value):
    """Convert string to datetime object, handling various formats"""
    if value is None:
        return None
    
    # If it's already a datetime object
    if isinstance(value, datetime):
        return value
    
    # If it's a string, try to parse it
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None
    
    return None

# Configuração do banco de dados
import os
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chamados_ti.db')

def init_db():
    """Inicializa o banco de dados"""
    # Garantir que o diretório existe
    os.makedirs(os.path.dirname(DATABASE) if os.path.dirname(DATABASE) else '.', exist_ok=True)
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
    # Tabela para nomes customizáveis das roles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_names (
            role_key TEXT PRIMARY KEY,
            label TEXT NOT NULL
        )
    ''')
    
    # Tabela de permissões de usuários
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
            FOREIGN KEY (criado_por) REFERENCES users (id),
            FOREIGN KEY (atribuido_para) REFERENCES users (id)
        )
    ''')
    
    # Criar usuário admin se não existir
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('Exponencial',))
    if cursor.fetchone()[0] == 0:
        admin_password = generate_password_hash('1234')
        cursor.execute('''
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', ('Exponencial', admin_password, 'admin'))
    # Ensure default role labels exist
    defaults = {
        'admin': 'Administrador',
        'tech': 'Técnico',
        'user': 'Usuário'
    }
    for k, v in defaults.items():
        cursor.execute('INSERT OR IGNORE INTO role_names (role_key, label) VALUES (?, ?)', (k, v))
    
    # Tabela de mensagens do chat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            lida BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
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

def get_user_role():
    """Retorna a role do usuário atual"""
    if 'user_id' not in session:
        return None
    return session.get('role')

def is_admin():
    """Verifica se usuário atual é admin"""
    return get_user_role() == 'admin'

def is_tech():
    """
    Verifica se usuário tem acesso técnico completo
    Diretor, Supervisor e Técnico veem TUDO
    """
    role = get_user_role()
    return role in ['admin', 'diretor', 'supervisor', 'tech']

def is_administrativo():
    """
    Verifica se usuário é administrativo
    Administrativo vê apenas Chamados e Chat
    """
    return get_user_role() == 'administrativo'

def can_access_chamados():
    """Verifica se pode acessar chamados"""
    role = get_user_role()
    return role in ['admin', 'diretor', 'supervisor', 'tech', 'administrativo', 'user']

def can_access_storage():
    """Verifica se pode acessar armazenamento de servidores"""
    role = get_user_role()
    return role in ['admin', 'diretor', 'supervisor', 'tech']

def can_access_funcoes():
    """Verifica se pode acessar funções"""
    return get_user_role() == 'admin'

def can_access_configuracoes():
    """Verifica se pode acessar configurações"""
    return get_user_role() == 'admin'

def can_access_chat():
    """Verifica se pode acessar chat"""
    role = get_user_role()
    return role in ['admin', 'diretor', 'supervisor', 'tech', 'administrativo']

def has_permission(permission_key):
    """
    Verifica se o usuário atual tem uma permissão específica
    """
    if 'user_id' not in session:
        return False
    
    user_id = session.get('user_id')
    
    # Admin sempre tem todas as permissões
    if session.get('role') == 'admin':
        return True
    
    conn = get_db_connection()
    perm = conn.execute(
        'SELECT enabled FROM user_permissions WHERE user_id = ? AND permission_key = ?',
        (user_id, permission_key)
    ).fetchone()
    conn.close()
    
    return perm is not None and perm['enabled'] == 1

def get_user_permissions(user_id):
    """
    Retorna lista de permissões do usuário
    """
    conn = get_db_connection()
    perms = conn.execute(
        'SELECT permission_key FROM user_permissions WHERE user_id = ? AND enabled = 1',
        (user_id,)
    ).fetchall()
    conn.close()
    
    return [p['permission_key'] for p in perms]

# Função para traduzir roles (labels customizáveis) e injetar permissões
@app.context_processor
def inject_permissions():
    """Injeta funções de permissão e role_label nos templates"""
    def role_label(role_key):
        """Retorna o label do role da tabela role_names ou valor padrão"""
        try:
            conn = get_db_connection()
            result = conn.execute('SELECT label FROM role_names WHERE role_key = ?', (role_key,)).fetchone()
            conn.close()
            if result and 'label' in result.keys():
                return result['label']
        except Exception:
            pass
        # Valores padrão caso não exista na tabela
        defaults = {
            'admin': 'Administrador',
            'diretor': 'Diretor',
            'supervisor': 'Supervisor',
            'tech': 'Técnico',
            'administrativo': 'Administrativo',
            'user': 'Usuário'
        }
        return defaults.get(role_key, role_key)
    
    return dict(
        role_label=role_label,
        can_access_chamados=can_access_chamados,
        can_access_storage=can_access_storage,
        can_access_funcoes=can_access_funcoes,
        can_access_configuracoes=can_access_configuracoes,
        can_access_chat=can_access_chat,
        has_permission=has_permission,
        is_admin=is_admin,
        is_tech=is_tech,
        is_administrativo=is_administrativo
    )

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
            session.clear()  # Limpar sessão anterior
            session.permanent = True  # Tornar sessão permanente (usa PERMANENT_SESSION_LIFETIME)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validações
        if password != confirm_password:
            flash('As senhas não coincidem!', 'danger')
            return render_template('login.html', show_register=True)
        
        conn = get_db_connection()
        
        # Verificar se usuário já existe
        if conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            flash('Nome de usuário já existe!', 'danger')
            conn.close()
            return render_template('login.html', show_register=True)
        
        if conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
            flash('Email já cadastrado!', 'danger')
            conn.close()
            return render_template('login.html', show_register=True)
        
        # Criar usuário
        password_hash = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, 'user'))
        conn.commit()
        conn.close()
        
        flash('Usuário criado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('login.html', show_register=True)

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
    
    # Chamados por prioridade
    chamados_por_prioridade = conn.execute('''
        SELECT prioridade, COUNT(*) as total
        FROM chamados
        GROUP BY prioridade
    ''').fetchall()
    chamados_por_prioridade = [{'prioridade': row[0], 'count': row[1]} for row in chamados_por_prioridade]
    
    # Chamados por categoria
    chamados_por_categoria = conn.execute('''
        SELECT categoria, COUNT(*) as total
        FROM chamados
        GROUP BY categoria
    ''').fetchall()
    chamados_por_categoria = [{'categoria': row[0], 'count': row[1]} for row in chamados_por_categoria]
    
    # Chamados recentes
    if is_tech():
        chamados_recentes_raw = conn.execute('''
            SELECT c.*, u.username as criador_nome
            FROM chamados c
            JOIN users u ON c.criado_por = u.id
            ORDER BY c.data_criacao DESC
            LIMIT 5
        ''').fetchall()
    else:
        chamados_recentes_raw = conn.execute('''
            SELECT c.*, u.username as criador_nome
            FROM chamados c
            JOIN users u ON c.criado_por = u.id
            WHERE c.criado_por = ?
            ORDER BY c.data_criacao DESC
            LIMIT 5
        ''', (session['user_id'],)).fetchall()
    
    # Converter para objetos com propriedades esperadas
    chamados_recentes = [convert_chamado_row(row) for row in chamados_recentes_raw]
    
    # Variáveis vazias para evitar erros no template
    meus_chamados = []
    chamados_atribuidos = []
    
    conn.close()
    
    return render_template('dashboard.html',
                         total_chamados=total_chamados,
                         chamados_abertos=chamados_abertos,
                         chamados_em_andamento=chamados_em_andamento,
                         chamados_resolvidos=chamados_resolvidos,
                         chamados_por_prioridade=chamados_por_prioridade,
                         chamados_por_categoria=chamados_por_categoria,
                         chamados_recentes=chamados_recentes,
                         meus_chamados=meus_chamados,
                         chamados_atribuidos=chamados_atribuidos)

@app.route('/chamados')
@login_required
def chamados():
    conn = get_db_connection()
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filtros
    status_filter = request.args.get('status', '')
    prioridade_filter = request.args.get('prioridade', '')
    categoria_filter = request.args.get('categoria', '')
    
    # Query base
    base_query = '''
        SELECT c.*, u.username as criador_nome, u2.username as tecnico_nome
        FROM chamados c
        JOIN users u ON c.criado_por = u.id
        LEFT JOIN users u2 ON c.atribuido_para = u2.id
    '''
    
    # Query para contar total
    count_query = 'SELECT COUNT(*) FROM chamados c JOIN users u ON c.criado_por = u.id'
    
    params = []
    conditions = []
    
    if not is_tech():
        conditions.append('c.criado_por = ?')
        params.append(session['user_id'])
    
    if status_filter:
        conditions.append('c.status = ?')
        params.append(status_filter)
    
    if prioridade_filter:
        conditions.append('c.prioridade = ?')
        params.append(prioridade_filter)
    
    if categoria_filter:
        conditions.append('c.categoria = ?')
        params.append(categoria_filter)
    
    if conditions:
        where_clause = ' WHERE ' + ' AND '.join(conditions)
        base_query += where_clause
        count_query += where_clause
    
    # Contar total de registros
    total = conn.execute(count_query, params).fetchone()[0]
    
    # Query com paginação
    query = base_query + ' ORDER BY c.data_criacao DESC LIMIT ? OFFSET ?'
    offset = (page - 1) * per_page
    paginated_params = params + [per_page, offset]
    
    chamados_list = conn.execute(query, paginated_params).fetchall()
    
    # Converter Rows para objetos com atributos esperados
    chamados_objects = [convert_chamado_row(row) for row in chamados_list]
    
    # Criar objeto de paginação
    chamados = Pagination(chamados_objects, page, per_page, total)
    
    # Listas para filtros
    categorias = conn.execute('SELECT DISTINCT categoria FROM chamados').fetchall()
    categorias = [cat[0] for cat in categorias]
    
    conn.close()
    return render_template('chamados.html', 
                         chamados=chamados,
                         categorias=categorias,
                         status_filter=status_filter,
                         prioridade_filter=prioridade_filter,
                         categoria_filter=categoria_filter)

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
    
    return render_template('chamado_form.html', action='novo')

@app.route('/chamados/<int:id>')
@login_required
def visualizar_chamado(id):
    conn = get_db_connection()
    chamado = conn.execute('''
        SELECT c.*, u.username as criador_nome, u2.username as tecnico_nome
        FROM chamados c
        JOIN users u ON c.criado_por = u.id
        LEFT JOIN users u2 ON c.atribuido_para = u2.id
        WHERE c.id = ?
    ''', (id,)).fetchone()
    
    if not chamado:
        flash('Chamado não encontrado!', 'danger')
        return redirect(url_for('chamados'))
    
    # Verificar permissão
    if not is_tech() and chamado['criado_por'] != session['user_id']:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('chamados'))
    
    # Converter Row para objeto com atributos esperados
    chamado_obj = convert_chamado_row(chamado)
    
    conn.close()
    return render_template('chamado_detalhes.html', chamado=chamado_obj)

@app.route('/chamados/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_chamado(id):
    conn = get_db_connection()
    chamado = conn.execute('SELECT * FROM chamados WHERE id = ?', (id,)).fetchone()
    
    if not chamado:
        flash('Chamado não encontrado!', 'danger')
        return redirect(url_for('chamados'))
    
    # Verificar permissão
    if not is_tech() and chamado['criado_por'] != session['user_id']:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('chamados'))
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']
        
        conn.execute('''
            UPDATE chamados 
            SET titulo = ?, descricao = ?, prioridade = ?, categoria = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (titulo, descricao, prioridade, categoria, id))
        
        if is_tech():
            status = request.form['status']
            atribuido_para = request.form.get('atribuido_para') or None
            solucao = request.form.get('solucao', '')
            
            conn.execute('''
                UPDATE chamados 
                SET status = ?, atribuido_para = ?, solucao = ?
                WHERE id = ?
            ''', (status, atribuido_para, solucao, id))
            
            if status == 'resolvido' and not chamado['data_resolucao']:
                conn.execute('''
                    UPDATE chamados 
                    SET data_resolucao = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (id,))
        
        conn.commit()
        conn.close()
        
        flash('Chamado atualizado com sucesso!', 'success')
        return redirect(url_for('visualizar_chamado', id=id))
    
    # Lista de técnicos
    tecnicos = conn.execute("SELECT * FROM users WHERE role IN ('admin', 'tech', 'diretor', 'supervisor')").fetchall()
    conn.close()
    
    return render_template('chamado_form.html',
                         chamado=chamado,
                         tecnicos=tecnicos,
                         action='editar')

@app.route('/chamados/<int:id>/deletar', methods=['POST'])
@login_required
def deletar_chamado(id):
    conn = get_db_connection()
    chamado = conn.execute('SELECT * FROM chamados WHERE id = ?', (id,)).fetchone()
    
    if not chamado:
        flash('Chamado não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('chamados'))
    
    # Verificar permissão:
    # Admin, Diretor e Supervisor podem deletar qualquer chamado
    # Usuário comum só pode deletar seus próprios chamados se estiverem em 'aberto'
    pode_deletar = False
    
    if session['role'] in ['admin', 'diretor', 'supervisor']:
        pode_deletar = True
    elif chamado['criado_por'] == session['user_id'] and chamado['status'] == 'aberto':
        pode_deletar = True
    
    if not pode_deletar:
        flash('Você não tem permissão para excluir este chamado!', 'danger')
        conn.close()
        return redirect(url_for('visualizar_chamado', id=id))
    
    # Salvar informações para a mensagem
    numero_chamado = chamado['id']
    titulo = chamado['titulo']
    
    conn.execute('DELETE FROM chamados WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash(f'Chamado #{numero_chamado} - "{titulo}" excluído com sucesso!', 'success')
    return redirect(url_for('chamados'))

# Aliases for blueprint compatibility
@app.route('/dashboard/index', endpoint='dashboard.index')
@login_required
def dashboard_index():
    return redirect(url_for('dashboard'))

@app.route('/chamado/index', endpoint='chamado.index')
@login_required
def chamado_index():
    return redirect(url_for('chamados'))

@app.route('/auth/login')
def auth_login():
    return redirect(url_for('login'))

@app.route('/chamado/novo', endpoint='chamado.novo')
@login_required
def chamado_novo():
    return redirect(url_for('novo_chamado'))

@app.route('/chamado/<int:id>', endpoint='chamado.visualizar')
@login_required
def chamado_visualizar(id):
    return redirect(url_for('visualizar_chamado', id=id))

@app.route('/chamado/<int:id>/editar', endpoint='chamado.editar')
@login_required
def chamado_editar(id):
    return redirect(url_for('editar_chamado', id=id))

@app.route('/chamado/<int:id>/deletar', methods=['POST'], endpoint='chamado.deletar')
@login_required
def chamado_deletar(id):
    # Usar código 307 para preservar o método POST no redirect
    return redirect(url_for('deletar_chamado', id=id), code=307)

@app.route('/perfil')
@login_required
def perfil():
    """Página de perfil do usuário"""
    # Validar sessão
    if 'user_id' not in session or session.get('user_id') is None:
        flash('Sessão inválida. Faça login novamente.', 'warning')
        return redirect(url_for('logout'))
    
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user_row:
        flash('Usuário não encontrado. Faça login novamente.', 'danger')
        conn.close()
        return redirect(url_for('logout'))
    
    # normalize to dict and add formatted date
    user = dict(user_row)
    if user:
        ca = user.get('created_at')
        from datetime import datetime
        if isinstance(ca, str) and ca:
            parsed = None
            try:
                parsed = datetime.fromisoformat(ca)
            except Exception:
                for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        parsed = datetime.strptime(ca, fmt)
                        break
                    except Exception:
                        parsed = None
            user['created_at_fmt'] = parsed.strftime('%d/%m/%Y') if parsed else ca
        else:
            user['created_at_fmt'] = ca
    
    # Estatísticas do usuário
    total_chamados = conn.execute('SELECT COUNT(*) FROM chamados WHERE criado_por = ?', (session['user_id'],)).fetchone()[0]
    chamados_abertos = conn.execute("SELECT COUNT(*) FROM chamados WHERE criado_por = ? AND status = 'aberto'", (session['user_id'],)).fetchone()[0]
    chamados_resolvidos = conn.execute("SELECT COUNT(*) FROM chamados WHERE criado_por = ? AND status = 'resolvido'", (session['user_id'],)).fetchone()[0]
    
    conn.close()
    
    return render_template('perfil.html', 
                         user=user,
                         total_chamados=total_chamados,
                         chamados_abertos=chamados_abertos,
                         chamados_resolvidos=chamados_resolvidos)

@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Editar perfil do usuário"""
    # Validar sessão
    if 'user_id' not in session or session.get('user_id') is None:
        flash('Sessão inválida. Faça login novamente.', 'warning')
        return redirect(url_for('logout'))
    
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user_row:
        flash('Usuário não encontrado. Faça login novamente.', 'danger')
        conn.close()
        return redirect(url_for('logout'))
    
    user = dict(user_row)

    # add created_at_fmt for the template
    if user:
        ca = user.get('created_at')
        from datetime import datetime
        if isinstance(ca, str) and ca:
            parsed = None
            try:
                parsed = datetime.fromisoformat(ca)
            except Exception:
                for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        parsed = datetime.strptime(ca, fmt)
                        break
                    except Exception:
                        parsed = None
            user['created_at_fmt'] = parsed.strftime('%d/%m/%Y') if parsed else ca
        else:
            user['created_at_fmt'] = ca
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        senha_atual = request.form.get('senha_atual', '')
        nova_senha = request.form.get('nova_senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        # Verificar se username já existe (exceto o próprio usuário)
        existing_user = conn.execute('SELECT id FROM users WHERE username = ? AND id != ?', (username, session['user_id'])).fetchone()
        if existing_user:
            flash('Nome de usuário já existe!', 'danger')
            conn.close()
            return render_template('editar_perfil.html', user=user)
        
        # Verificar se email já existe (exceto o próprio usuário)
        existing_email = conn.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, session['user_id'])).fetchone()
        if existing_email:
            flash('Email já cadastrado!', 'danger')
            conn.close()
            return render_template('editar_perfil.html', user=user)
        
        # Atualizar dados básicos
        conn.execute('''
            UPDATE users 
            SET username = ?, email = ?
            WHERE id = ?
        ''', (username, email, session['user_id']))
        
        # Atualizar senha se fornecida
        if nova_senha:
            if not senha_atual or not check_password_hash(user['password_hash'], senha_atual):
                flash('Senha atual incorreta!', 'danger')
                conn.close()
                return render_template('editar_perfil.html', user=user)
            
            if nova_senha != confirmar_senha:
                flash('Nova senha e confirmação não coincidem!', 'danger')
                conn.close()
                return render_template('editar_perfil.html', user=user)
            
            password_hash = generate_password_hash(nova_senha)
            conn.execute('''
                UPDATE users 
                SET password_hash = ?
                WHERE id = ?
            ''', (password_hash, session['user_id']))
        
        conn.commit()
        conn.close()
        
        # Atualizar sessão
        session['username'] = username
        
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('perfil'))
    
    conn.close()
    return render_template('editar_perfil.html', user=user)

@app.route('/configuracoes')
@login_required
def configuracoes():
    """Página de configurações do sistema"""
    if session['role'] != 'admin':
        flash('Acesso negado! Apenas administradores podem acessar as configurações.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    
    # Estatísticas do sistema
    total_usuarios = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_chamados = conn.execute('SELECT COUNT(*) FROM chamados').fetchone()[0]
    total_servidores = conn.execute('SELECT COUNT(*) FROM servidores').fetchone()[0]
    
    # Usuários por role
    usuarios_por_role = conn.execute('''
        SELECT role, COUNT(*) as total
        FROM users
        GROUP BY role
    ''').fetchall()
    
    conn.close()
    
    # Data atual para exibição (substitui uso de moment.js no template)
    last_update = datetime.now().strftime('%d/%m/%Y')

    return render_template('configuracoes.html',
                         total_usuarios=total_usuarios,
                         total_chamados=total_chamados,
                         total_servidores=total_servidores,
                         usuarios_por_role=usuarios_por_role,
                         last_update=last_update)

@app.route('/configuracoes/usuarios')
@login_required
def gerenciar_usuarios():
    """Gerenciar usuários do sistema"""
    if session['role'] != 'admin':
        flash('Acesso negado! Apenas administradores podem gerenciar usuários.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    usuarios_raw = conn.execute('''
        SELECT u.id, u.username, u.email, u.role, u.created_at, u.is_active, u.funcao_id, f.nome as funcao_nome
        FROM users u
        LEFT JOIN funcoes f ON u.funcao_id = f.id
        ORDER BY u.created_at DESC
    ''').fetchall()
    
    # Buscar todas as funções disponíveis
    funcoes = conn.execute('SELECT * FROM funcoes ORDER BY nivel_acesso DESC').fetchall()
    conn.close()
    
    return render_template('gerenciar_usuarios.html', usuarios=usuarios_raw, funcoes=funcoes)

    # Converter created_at (string) para datetime quando possível, para que o template possa usar .strftime
    from datetime import datetime
    usuarios = []
    for u in usuarios_raw:
        # sqlite3.Row -> dict
        row = dict(u)
        ca = row.get('created_at')
        if isinstance(ca, str) and ca:
            parsed = None
            # tentar formatos comuns
            try:
                parsed = datetime.fromisoformat(ca)
            except Exception:
                for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        parsed = datetime.strptime(ca, fmt)
                        break
                    except Exception:
                        parsed = None
            if parsed:
                row['created_at'] = parsed
                # criar também uma string formatada segura para usar no template
                row['created_at_fmt'] = parsed.strftime('%d/%m/%Y %H:%M')
            else:
                # mantemos como string se não foi possível parsear
                row['created_at'] = ca
                row['created_at_fmt'] = ca

        usuarios.append(row)

    return render_template('gerenciar_usuarios.html', usuarios=usuarios)

@app.route('/configuracoes/usuarios/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_usuario(id):
    """Ativar/desativar usuário"""
    if session['role'] != 'admin':
        flash('Acesso negado!', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    
    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('gerenciar_usuarios'))
    
    # Não permitir desativar o próprio usuário
    if id == session['user_id']:
        flash('Você não pode desativar sua própria conta!', 'danger')
        conn.close()
        return redirect(url_for('gerenciar_usuarios'))
    
    # Toggle do status
    novo_status = 0 if usuario['is_active'] else 1
    conn.execute('UPDATE users SET is_active = ? WHERE id = ?', (novo_status, id))
    conn.commit()
    conn.close()
    
    status_texto = 'ativado' if novo_status else 'desativado'
    flash(f'Usuário {status_texto} com sucesso!', 'success')
    return redirect(url_for('gerenciar_usuarios'))


@app.route('/configuracoes/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    """Editar usuário (apenas admin)"""
    if session['role'] != 'admin':
        flash('Acesso negado! Apenas administradores podem editar usuários.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()

    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('gerenciar_usuarios'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        funcao_id = request.form.get('funcao_id')
        if funcao_id == '':
            funcao_id = None
        elif funcao_id:
            try:
                funcao_id = int(funcao_id)
            except ValueError:
                funcao_id = None
        password = request.form.get('password', '').strip()

        # Validações básicas
        existing = conn.execute('SELECT id FROM users WHERE username = ? AND id != ?', (username, id)).fetchone()
        if existing:
            flash('Nome de usuário já em uso por outro usuário.', 'danger')
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        existing_email = conn.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, id)).fetchone()
        if existing_email:
            flash('Email já em uso por outro usuário.', 'danger')
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        # Atualiza campos
        conn.execute('UPDATE users SET username = ?, email = ?, role = ?, funcao_id = ? WHERE id = ?', (username, email, role, funcao_id, id))

        # Atualiza senha se enviada
        if password:
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(password)
            conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, id))

        # Salvar permissões granulares
        permissions = [
            'view_chamados', 'create_chamados', 'edit_chamados', 'delete_chamados',
            'assign_chamados', 'manage_infrastructure', 'manage_users', 'access_chat'
        ]
        
        # Remover permissões antigas do usuário
        conn.execute('DELETE FROM user_permissions WHERE user_id = ?', (id,))
        
        # Inserir novas permissões
        for perm in permissions:
            field_name = f'permission_{perm}'
            value = request.form.get(field_name, '0')
            enabled = 1 if value == '1' else 0
            
            if enabled:  # Só salvar permissões ativas
                conn.execute(
                    'INSERT INTO user_permissions (user_id, permission_key, enabled) VALUES (?, ?, ?)',
                    (id, perm, enabled)
                )

        conn.commit()
        conn.close()
        flash('Usuário e permissões atualizados com sucesso!', 'success')
        return redirect(url_for('gerenciar_usuarios'))

    # Buscar todas as funções disponíveis
    funcoes = conn.execute('SELECT * FROM funcoes ORDER BY nivel_acesso DESC').fetchall()
    
    # Buscar permissões do usuário
    try:
        user_permissions = conn.execute(
            'SELECT permission_key FROM user_permissions WHERE user_id = ? AND enabled = 1',
            (id,)
        ).fetchall()
        # Converter para lista de strings
        permissions_list = [perm['permission_key'] for perm in user_permissions] if user_permissions else []
    except Exception as e:
        print(f"Erro ao buscar permissões: {e}")
        permissions_list = []
    
    conn.close()
    return render_template('editar_usuario.html', usuario=usuario, funcoes=funcoes, user_permissions=permissions_list)

# ==========================================
# CHAT DE SUPORTE - Estilo WhatsApp
# ==========================================

@app.route('/chat')
@login_required
def chat():
    """Página principal do chat"""
    return render_template('chat.html')

@app.route('/api/chat/mensagens', methods=['GET'])
def get_mensagens():
    """Obter mensagens do chat"""
    # Verificar se está logado
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    conn = get_db_connection()
    
    # Pegar últimas 100 mensagens
    mensagens = conn.execute('''
        SELECT id, user_id, username, mensagem, data_envio, lida
        FROM chat_mensagens
        ORDER BY data_envio DESC
        LIMIT 100
    ''').fetchall()
    
    conn.close()
    
    # Converter para lista (ordem cronológica)
    mensagens_list = []
    for msg in reversed(mensagens):
        mensagens_list.append({
            'id': msg['id'],
            'user_id': msg['user_id'],
            'username': msg['username'],
            'mensagem': msg['mensagem'],
            'data_envio': msg['data_envio'],
            'lida': msg['lida'],
            'is_me': msg['user_id'] == session.get('user_id')
        })
    
    return jsonify({'mensagens': mensagens_list})

@app.route('/api/chat/enviar', methods=['POST'])
def enviar_mensagem():
    """Enviar mensagem no chat"""
    # Verificar se está logado
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    mensagem = data.get('mensagem', '').strip()
    
    if not mensagem:
        return jsonify({'error': 'Mensagem vazia'}), 400
    
    conn = get_db_connection()
    
    # Inserir mensagem
    conn.execute('''
        INSERT INTO chat_mensagens (user_id, username, mensagem)
        VALUES (?, ?, ?)
    ''', (session['user_id'], session['username'], mensagem))
    
    conn.commit()
    
    # Pegar a mensagem inserida
    msg = conn.execute('''
        SELECT id, user_id, username, mensagem, data_envio, lida
        FROM chat_mensagens
        WHERE id = last_insert_rowid()
    ''').fetchone()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'mensagem': {
            'id': msg['id'],
            'user_id': msg['user_id'],
            'username': msg['username'],
            'mensagem': msg['mensagem'],
            'data_envio': msg['data_envio'],
            'is_me': True
        }
    })

@app.route('/api/chat/marcar-lidas', methods=['POST'])
def marcar_lidas():
    """Marcar mensagens como lidas"""
    # Verificar se está logado
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    conn = get_db_connection()
    
    # Marcar todas as mensagens como lidas (exceto as do próprio usuário)
    conn.execute('''
        UPDATE chat_mensagens
        SET lida = 1
        WHERE user_id != ? AND lida = 0
    ''', (session['user_id'],))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    print("🚀 Sistema de Chamados TI iniciado!")
    print("📱 Acesse: http://127.0.0.1:5000")
    print("🔑 Login: Exponencial / 1234")
    
    # Detectar se está em produção (Render, Heroku, etc)
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    host = '0.0.0.0' if not debug else '127.0.0.1'
    
    app.run(debug=debug, host=host, port=port)
