from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from functools import wraps

role_bp = Blueprint('role', __name__, url_prefix='/roles')

# Decorator para verificar se o usuário pode gerenciar cargos
def role_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        if not current_user.can_manage_roles:
            flash('Você não tem permissão para gerenciar cargos!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Definição dos cargos disponíveis e suas permissões
ROLES_CONFIG = {
    'admin': {
        'label': 'Administrador',
        'description': 'Acesso total ao sistema, incluindo gerenciamento de usuários e cargos',
        'permissions': [
            'Gerenciar usuários',
            'Gerenciar cargos',
            'Gerenciar chamados (todos)',
            'Gerenciar infraestrutura',
            'Gerenciar servidores',
            'Acessar relatórios completos',
            'Deletar registros'
        ],
        'color': 'danger',
        'icon': 'bi-shield-fill-exclamation'
    },
    'role_manager': {
        'label': 'Gerente de Cargos',
        'description': 'Pode gerenciar cargos e permissões de usuários',
        'permissions': [
            'Gerenciar cargos',
            'Visualizar usuários',
            'Atribuir cargos a usuários',
            'Ver chamados (todos)',
            'Ver infraestrutura'
        ],
        'color': 'primary',
        'icon': 'bi-person-gear'
    },
    'tech': {
        'label': 'Técnico',
        'description': 'Pode gerenciar chamados e infraestrutura',
        'permissions': [
            'Gerenciar chamados (atribuídos)',
            'Gerenciar infraestrutura',
            'Gerenciar servidores',
            'Ver relatórios básicos'
        ],
        'color': 'info',
        'icon': 'bi-wrench'
    },
    'user': {
        'label': 'Usuário',
        'description': 'Pode criar e visualizar próprios chamados',
        'permissions': [
            'Criar chamados',
            'Ver próprios chamados',
            'Editar próprios chamados',
            'Ver dashboard básico'
        ],
        'color': 'secondary',
        'icon': 'bi-person'
    }
}

@role_bp.route('/')
@login_required
@role_manager_required
def index():
    """Lista todos os cargos e suas configurações"""
    return render_template('role_manager.html', roles=ROLES_CONFIG)

@role_bp.route('/usuarios')
@login_required
@role_manager_required
def listar_usuarios():
    """Lista todos os usuários e seus cargos"""
    usuarios = User.query.order_by(User.username).all()
    return render_template('role_usuarios.html', usuarios=usuarios, roles=ROLES_CONFIG)

@role_bp.route('/usuarios/<int:user_id>/alterar-cargo', methods=['POST'])
@login_required
@role_manager_required
def alterar_cargo(user_id):
    """Altera o cargo de um usuário"""
    usuario = User.query.get_or_404(user_id)
    novo_cargo = request.form.get('cargo')
    
    # Validar se o cargo existe
    if novo_cargo not in ROLES_CONFIG:
        flash('Cargo inválido!', 'danger')
        return redirect(url_for('role.listar_usuarios'))
    
    # Impedir que o usuário altere seu próprio cargo
    if usuario.id == current_user.id:
        flash('Você não pode alterar seu próprio cargo!', 'warning')
        return redirect(url_for('role.listar_usuarios'))
    
    # Apenas admin pode criar outros admins
    if novo_cargo == 'admin' and not current_user.is_admin:
        flash('Apenas administradores podem criar outros administradores!', 'danger')
        return redirect(url_for('role.listar_usuarios'))
    
    cargo_antigo = usuario.role
    usuario.role = novo_cargo
    db.session.commit()
    
    flash(f'Cargo de {usuario.username} alterado de "{ROLES_CONFIG[cargo_antigo]["label"]}" para "{ROLES_CONFIG[novo_cargo]["label"]}"!', 'success')
    return redirect(url_for('role.listar_usuarios'))

@role_bp.route('/api/roles', methods=['GET'])
@login_required
@role_manager_required
def api_roles():
    """API para obter informações sobre os cargos"""
    return jsonify(ROLES_CONFIG)

@role_bp.route('/api/usuarios', methods=['GET'])
@login_required
@role_manager_required
def api_usuarios():
    """API para obter lista de usuários e seus cargos"""
    usuarios = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'role': u.role,
        'role_label': ROLES_CONFIG.get(u.role, {}).get('label', u.role),
        'is_active': u.is_active
    } for u in usuarios])

