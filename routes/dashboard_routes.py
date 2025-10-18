from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.chamado import Chamado
from models.infraestrutura import Infraestrutura
from models.user import User
from models import db
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Estatísticas gerais
    total_chamados = Chamado.query.count()
    chamados_abertos = Chamado.query.filter_by(status='aberto').count()
    chamados_em_andamento = Chamado.query.filter_by(status='em_andamento').count()
    chamados_resolvidos = Chamado.query.filter_by(status='resolvido').count()
    
    # Chamados por prioridade
    chamados_por_prioridade = db.session.query(
        Chamado.prioridade, 
        func.count(Chamado.id)
    ).group_by(Chamado.prioridade).all()
    chamados_por_prioridade = [{'prioridade': row[0], 'count': row[1]} for row in chamados_por_prioridade]
    
    # Chamados por categoria
    chamados_por_categoria = db.session.query(
        Chamado.categoria,
        func.count(Chamado.id)
    ).group_by(Chamado.categoria).all()
    chamados_por_categoria = [{'categoria': row[0], 'count': row[1]} for row in chamados_por_categoria]
    
    # Chamados recentes
    chamados_recentes = Chamado.query.order_by(Chamado.data_criacao.desc()).limit(5).all()
    
    # Equipamentos com mais problemas
    equipamentos_problemas = db.session.query(
        Infraestrutura.nome,
        func.count(Chamado.id).label('total_chamados')
    ).join(Chamado).group_by(Infraestrutura.id).order_by(
        func.count(Chamado.id).desc()
    ).limit(5).all()
    equipamentos_problemas = [{'nome': row[0], 'total_chamados': row[1]} for row in equipamentos_problemas]
    
    # Chamados do usuário atual (se não for admin/tech)
    meus_chamados = []
    if not current_user.is_tech:
        meus_chamados = Chamado.query.filter_by(criado_por=current_user.id).order_by(
            Chamado.data_criacao.desc()
        ).limit(5).all()
    
    # Chamados atribuídos ao técnico atual
    chamados_atribuidos = []
    if current_user.is_tech:
        chamados_atribuidos = Chamado.query.filter_by(atribuido_para=current_user.id).order_by(
            Chamado.data_criacao.desc()
        ).limit(5).all()
    
    return render_template('dashboard.html',
                         total_chamados=total_chamados,
                         chamados_abertos=chamados_abertos,
                         chamados_em_andamento=chamados_em_andamento,
                         chamados_resolvidos=chamados_resolvidos,
                         chamados_por_prioridade=chamados_por_prioridade,
                         chamados_por_categoria=chamados_por_categoria,
                         chamados_recentes=chamados_recentes,
                         equipamentos_problemas=equipamentos_problemas,
                         meus_chamados=meus_chamados,
                         chamados_atribuidos=chamados_atribuidos)

@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API para estatísticas em tempo real"""
    stats = {
        'total_chamados': Chamado.query.count(),
        'chamados_abertos': Chamado.query.filter_by(status='aberto').count(),
        'chamados_em_andamento': Chamado.query.filter_by(status='em_andamento').count(),
        'chamados_resolvidos': Chamado.query.filter_by(status='resolvido').count(),
        'equipamentos_ativos': Infraestrutura.query.filter_by(status='ativo').count(),
        'equipamentos_manutencao': Infraestrutura.query.filter_by(status='manutencao').count()
    }
    return jsonify(stats)

