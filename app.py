from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import math
from routes.funcao_routes import funcao_bp
from routes.servidor_storage_routes import servidor_storage_bp

app = Flask(__name__)

# Configurações de segurança e sessão
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-super-segura-2024')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Sessão dura 24 horas
app.config['SESSION_COOKIE_SECURE'] = False  # True apenas em HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Registrando blueprints
app.register_blueprint(funcao_bp)
app.register_blueprint(servidor_storage_bp)

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

class MockEquipamento:
    """Mock equipamento object to match template expectations"""
    def __init__(self, id, nome, tipo, status, localizacao, marca, modelo):
        self.id = id
        self.nome = nome
        self.tipo = tipo
        self.status = status
        self.localizacao = localizacao
        self.marca = marca
        self.modelo = modelo
        
    @property
    def tipo_icon(self):
        icons = {
            'computador': '💻',
            'impressora': '🖨️',
            'servidor': '🖥️',
            'roteador': '📡',
            'switch': '🔌',
            'telefone': '📞',
            'monitor': '🖥️',
            'outros': '⚙️'
        }
        return icons.get(self.tipo.lower(), '⚙️')
    
    @property
    def status_class(self):
        classes = {
            'ativo': 'success',
            'inativo': 'danger',
            'manutencao': 'warning'
        }
        return classes.get(self.status, 'secondary')

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
            
            # Add equipamento if exists
            if 'equipamento_id' in row.keys() and row['equipamento_id'] and 'equipamento_nome' in row.keys() and row['equipamento_nome']:
                self.equipamento = MockEquipamento(
                    id=row['equipamento_id'],
                    nome=row['equipamento_nome'],
                    tipo=row['equipamento_tipo'] if 'equipamento_tipo' in row.keys() else 'outros',
                    status=row['equipamento_status'] if 'equipamento_status' in row.keys() else 'ativo',
                    localizacao=row['equipamento_localizacao'] if 'equipamento_localizacao' in row.keys() else '',
                    marca=row['equipamento_marca'] if 'equipamento_marca' in row.keys() else '',
                    modelo=row['equipamento_modelo'] if 'equipamento_modelo' in row.keys() else ''
                )
            else:
                self.equipamento = None
        
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

def is_admin():
    """Verifica se usuário atual é admin"""
    if 'user_id' not in session:
        return False
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        return user is not None and user['role'] == 'admin'
    except Exception:
        return False

def is_tech():
    """Verifica se usuário atual é técnico ou admin"""
    if 'user_id' not in session:
        return False
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        return user is not None and user['role'] in ['admin', 'tech']
    except Exception:
        return False

# Função para traduzir roles (labels customizáveis)
@app.context_processor
def inject_role_label():
    """Injeta a função role_label nos templates"""
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
            'tech': 'Técnico',
            'user': 'Usuário'
        }
        return defaults.get(role_key, role_key)
    return dict(role_label=role_label)

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
    
    # Equipamentos com mais problemas
    equipamentos_problemas = conn.execute('''
        SELECT i.nome, COUNT(c.id) as total_chamados
        FROM infraestrutura i
        LEFT JOIN chamados c ON i.id = c.equipamento_id
        WHERE i.status = 'ativo'
        GROUP BY i.id, i.nome
        HAVING COUNT(c.id) > 0
        ORDER BY total_chamados DESC
        LIMIT 5
    ''').fetchall()
    equipamentos_problemas = [{'nome': row[0], 'total_chamados': row[1]} for row in equipamentos_problemas]
    
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
                         chamados_atribuidos=chamados_atribuidos,
                         equipamentos_problemas=equipamentos_problemas)

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
        SELECT c.*, u.username as criador_nome, u2.username as tecnico_nome,
               i.nome as equipamento_nome, i.tipo as equipamento_tipo, 
               i.status as equipamento_status, i.localizacao as equipamento_localizacao,
               i.marca as equipamento_marca, i.modelo as equipamento_modelo
        FROM chamados c
        JOIN users u ON c.criado_por = u.id
        LEFT JOIN users u2 ON c.atribuido_para = u2.id
        LEFT JOIN infraestrutura i ON c.equipamento_id = i.id
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
        equipamento_id = request.form.get('equipamento_id') or None
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO chamados (titulo, descricao, prioridade, categoria, criado_por, equipamento_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (titulo, descricao, prioridade, categoria, session['user_id'], equipamento_id))
        conn.commit()
        conn.close()
        
        flash('Chamado criado com sucesso!', 'success')
        return redirect(url_for('chamados'))
    
    # Lista de equipamentos para seleção
    conn = get_db_connection()
    equipamentos = conn.execute("SELECT * FROM infraestrutura WHERE status = 'ativo'").fetchall()
    conn.close()
    
    return render_template('chamado_form.html', 
                         equipamentos=equipamentos,
                         action='novo')

@app.route('/chamados/<int:id>')
@login_required
def visualizar_chamado(id):
    conn = get_db_connection()
    chamado = conn.execute('''
        SELECT c.*, u.username as criador_nome, u2.username as tecnico_nome, 
               i.nome as equipamento_nome, i.tipo as equipamento_tipo, 
               i.status as equipamento_status, i.localizacao as equipamento_localizacao,
               i.marca as equipamento_marca, i.modelo as equipamento_modelo
        FROM chamados c
        JOIN users u ON c.criado_por = u.id
        LEFT JOIN users u2 ON c.atribuido_para = u2.id
        LEFT JOIN infraestrutura i ON c.equipamento_id = i.id
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
        equipamento_id = request.form.get('equipamento_id') or None
        
        conn.execute('''
            UPDATE chamados 
            SET titulo = ?, descricao = ?, prioridade = ?, categoria = ?, equipamento_id = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (titulo, descricao, prioridade, categoria, equipamento_id, id))
        
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
    
    # Lista de equipamentos e técnicos
    equipamentos = conn.execute("SELECT * FROM infraestrutura WHERE status = 'ativo'").fetchall()
    tecnicos = conn.execute("SELECT * FROM users WHERE role IN ('admin', 'tech')").fetchall()
    conn.close()
    
    return render_template('chamado_form.html',
                         chamado=chamado,
                         equipamentos=equipamentos,
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
    # Admin pode deletar qualquer chamado
    # Usuário comum só pode deletar seus próprios chamados se estiverem em 'aberto'
    pode_deletar = False
    
    if session['role'] == 'admin':
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

@app.route('/infraestrutura')
@app.route('/infra')
@login_required
def infraestrutura():
    if not is_tech():
        flash('Acesso negado!', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filtros
    tipo_filter = request.args.get('tipo', '')
    status_filter = request.args.get('status', '')
    localizacao_filter = request.args.get('localizacao', '')
    
    # Query base
    base_query = 'SELECT * FROM infraestrutura'
    count_query = 'SELECT COUNT(*) FROM infraestrutura'
    
    params = []
    conditions = []
    
    if tipo_filter:
        conditions.append('tipo = ?')
        params.append(tipo_filter)
    
    if status_filter:
        conditions.append('status = ?')
        params.append(status_filter)
    
    if localizacao_filter:
        conditions.append('localizacao LIKE ?')
        params.append(f'%{localizacao_filter}%')
    
    if conditions:
        where_clause = ' WHERE ' + ' AND '.join(conditions)
        base_query += where_clause
        count_query += where_clause
    
    # Contar total de registros
    total = conn.execute(count_query, params).fetchone()[0]
    
    # Query com paginação
    query = base_query + ' ORDER BY nome LIMIT ? OFFSET ?'
    offset = (page - 1) * per_page
    paginated_params = params + [per_page, offset]
    
    equipamentos_list = conn.execute(query, paginated_params).fetchall()
    
    # Criar objeto de paginação
    equipamentos = Pagination(equipamentos_list, page, per_page, total)
    
    # Listas para filtros
    tipos = conn.execute('SELECT DISTINCT tipo FROM infraestrutura').fetchall()
    tipos = [tipo[0] for tipo in tipos]
    
    localizacoes = conn.execute('SELECT DISTINCT localizacao FROM infraestrutura').fetchall()
    localizacoes = [loc[0] for loc in localizacoes]
    
    conn.close()
    
    return render_template('infraestrutura.html',
                         equipamentos=equipamentos,
                         tipos=tipos,
                         localizacoes=localizacoes,
                         tipo_filter=tipo_filter,
                         status_filter=status_filter,
                         localizacao_filter=localizacao_filter)

# Aliases for blueprint compatibility
@app.route('/dashboard/index', endpoint='dashboard.index')
@login_required
def dashboard_index():
    return redirect(url_for('dashboard'))

@app.route('/chamado/index', endpoint='chamado.index')
@login_required
def chamado_index():
    return redirect(url_for('chamados'))

@app.route('/infra/index', endpoint='infra.index')
@login_required
def infra_index():
    return redirect(url_for('infraestrutura'))

@app.route('/auth/login')
def auth_login():
    return redirect(url_for('login'))

# Additional aliases for blueprint compatibility
@app.route('/infra/novo', endpoint='infra.novo')
@login_required
def infra_novo():
    return redirect(url_for('novo_equipamento'))

@app.route('/infra/<int:id>', endpoint='infra.visualizar')
@login_required
def infra_visualizar(id):
    return redirect(url_for('visualizar_equipamento', id=id))

@app.route('/infra/<int:id>/editar', endpoint='infra.editar')
@login_required
def infra_editar(id):
    return redirect(url_for('editar_equipamento', id=id))

@app.route('/infra/<int:id>/deletar', methods=['POST'], endpoint='infra.deletar')
@login_required
def infra_deletar(id):
    # Only admins may delete equipment
    if session.get('role') != 'admin':
        flash('Acesso negado!', 'danger')
        return redirect(url_for('infraestrutura'))

    conn = get_db_connection()
    # Check for associated chamados
    chamados_count = conn.execute('SELECT COUNT(*) FROM chamados WHERE equipamento_id = ?', (id,)).fetchone()[0]
    if chamados_count > 0:
        flash(f'Não é possível deletar equipamento com {chamados_count} chamado(s) associado(s)!', 'danger')
        conn.close()
        return redirect(url_for('visualizar_equipamento', id=id))

    try:
        conn.execute('DELETE FROM infraestrutura WHERE id = ?', (id,))
        conn.commit()
        flash('Equipamento deletado com sucesso!', 'success')
    except Exception:
        conn.rollback()
        flash('Erro ao deletar equipamento!', 'danger')
    finally:
        conn.close()

    return redirect(url_for('infraestrutura'))


# Backwards-compatible alias: some templates or integrations may call url_for('deletar_equipamento', id=...)
# Provide an endpoint with that name which redirects to the actual infra deletion endpoint.
@app.route('/deletar_equipamento/<int:id>', methods=['POST'], endpoint='deletar_equipamento')
@login_required
def deletar_equipamento_alias(id):
    # Preserve method semantics when forwarding: use 307 Temporary Redirect so POST stays POST
    return redirect(url_for('infra.deletar', id=id), code=307)

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
    return redirect(url_for('deletar_chamado', id=id))

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
        numero_serie = request.form.get('numero_serie', '')
        localizacao = request.form['localizacao']
        responsavel = request.form.get('responsavel', '')
        status = request.form['status']
        data_aquisicao = request.form.get('data_aquisicao')
        observacoes = request.form.get('observacoes', '')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO infraestrutura (nome, tipo, marca, modelo, numero_serie, localizacao, responsavel, status, data_aquisicao, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, tipo, marca, modelo, numero_serie, localizacao, responsavel, status, data_aquisicao, observacoes))
        conn.commit()
        conn.close()
        
        flash('Equipamento cadastrado com sucesso!', 'success')
        return redirect(url_for('infraestrutura'))
    
    return render_template('infra_form.html', action='novo')

@app.route('/infraestrutura/<int:id>')
@login_required
def visualizar_equipamento(id):
    if not is_tech():
        flash('Acesso negado!', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    equipamento = conn.execute('SELECT * FROM infraestrutura WHERE id = ?', (id,)).fetchone()
    
    if not equipamento:
        flash('Equipamento não encontrado!', 'danger')
        return redirect(url_for('infraestrutura'))
    
    # Buscar chamados relacionados
    chamados = conn.execute('''
        SELECT c.*, u.username as criador_nome
        FROM chamados c
        JOIN users u ON c.criado_por = u.id
        WHERE c.equipamento_id = ?
        ORDER BY c.data_criacao DESC
        LIMIT 10
    ''', (id,)).fetchall()
    
    conn.close()
    
    return render_template('infra_detalhes.html',
                         equipamento=equipamento,
                         chamados=chamados)

@app.route('/infraestrutura/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_equipamento(id):
    if not is_tech():
        flash('Acesso negado!', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    equipamento = conn.execute('SELECT * FROM infraestrutura WHERE id = ?', (id,)).fetchone()
    
    if not equipamento:
        flash('Equipamento não encontrado!', 'danger')
        return redirect(url_for('infraestrutura'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        marca = request.form.get('marca', '')
        modelo = request.form.get('modelo', '')
        numero_serie = request.form.get('numero_serie', '')
        localizacao = request.form['localizacao']
        responsavel = request.form.get('responsavel', '')
        status = request.form['status']
        data_aquisicao = request.form.get('data_aquisicao')
        observacoes = request.form.get('observacoes', '')
        
        conn.execute('''
            UPDATE infraestrutura 
            SET nome = ?, tipo = ?, marca = ?, modelo = ?, numero_serie = ?, 
                localizacao = ?, responsavel = ?, status = ?, data_aquisicao = ?, 
                observacoes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (nome, tipo, marca, modelo, numero_serie, localizacao, responsavel, 
              status, data_aquisicao, observacoes, id))
        
        conn.commit()
        conn.close()
        
        flash('Equipamento atualizado com sucesso!', 'success')
        return redirect(url_for('visualizar_equipamento', id=id))
    
    conn.close()
    return render_template('infra_form.html',
                         equipamento=equipamento,
                         action='editar')

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
    total_equipamentos = conn.execute('SELECT COUNT(*) FROM infraestrutura').fetchone()[0]
    
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
                         total_equipamentos=total_equipamentos,
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
        conn.execute('UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?', (username, email, role, id))

        # Atualiza senha se enviada
        if password:
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(password)
            conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, id))

        conn.commit()
        conn.close()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('gerenciar_usuarios'))

    conn.close()
    return render_template('editar_usuario.html', usuario=usuario)

# ==========================================
# CHAT DE SUPORTE - Estilo WhatsApp
# ==========================================

@app.route('/chat')
@login_required
def chat():
    """Página principal do chat"""
    return render_template('chat.html')

@app.route('/api/chat/mensagens', methods=['GET'])
@login_required
def get_mensagens():
    """Obter mensagens do chat"""
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
@login_required
def enviar_mensagem():
    """Enviar mensagem no chat"""
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
@login_required
def marcar_lidas():
    """Marcar mensagens como lidas"""
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
