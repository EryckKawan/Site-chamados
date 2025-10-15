from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.chamado import Chamado
from models.infraestrutura import Infraestrutura
from models.user import User
from models import db
from datetime import datetime

chamado_bp = Blueprint('chamado', __name__)

@chamado_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    prioridade_filter = request.args.get('prioridade', '')
    categoria_filter = request.args.get('categoria', '')
    
    query = Chamado.query
    
    # Filtros
    if status_filter:
        query = query.filter_by(status=status_filter)
    if prioridade_filter:
        query = query.filter_by(prioridade=prioridade_filter)
    if categoria_filter:
        query = query.filter_by(categoria=categoria_filter)
    
    # Se não for admin/tech, mostrar apenas seus chamados
    if not current_user.is_tech:
        query = query.filter_by(criado_por=current_user.id)
    
    chamados = query.order_by(Chamado.data_criacao.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Listas para filtros
    categorias = db.session.query(Chamado.categoria).distinct().all()
    categorias = [cat[0] for cat in categorias]
    
    return render_template('chamados.html', 
                         chamados=chamados,
                         categorias=categorias,
                         status_filter=status_filter,
                         prioridade_filter=prioridade_filter,
                         categoria_filter=categoria_filter)

@chamado_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']
        equipamento_id = request.form.get('equipamento_id') or None
        
        chamado = Chamado(
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            categoria=categoria,
            criado_por=current_user.id,
            equipamento_id=equipamento_id
        )
        
        try:
            db.session.add(chamado)
            db.session.commit()
            flash('Chamado criado com sucesso!', 'success')
            return redirect(url_for('chamado.index'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar chamado!', 'danger')
    
    # Lista de equipamentos para seleção
    equipamentos = Infraestrutura.query.filter_by(status='ativo').all()
    
    return render_template('chamado_form.html', 
                         equipamentos=equipamentos,
                         action='novo')

@chamado_bp.route('/<int:id>')
@login_required
def visualizar(id):
    chamado = Chamado.query.get_or_404(id)
    
    # Verificar permissão
    if not current_user.is_tech and chamado.criado_por != current_user.id:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('chamado.index'))
    
    return render_template('chamado_detalhes.html', chamado=chamado)

@chamado_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    chamado = Chamado.query.get_or_404(id)
    
    # Verificar permissão
    if not current_user.is_tech and chamado.criado_por != current_user.id:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('chamado.index'))
    
    if request.method == 'POST':
        chamado.titulo = request.form['titulo']
        chamado.descricao = request.form['descricao']
        chamado.prioridade = request.form['prioridade']
        chamado.categoria = request.form['categoria']
        chamado.equipamento_id = request.form.get('equipamento_id') or None
        
        if current_user.is_tech:
            chamado.status = request.form['status']
            chamado.atribuido_para = request.form.get('atribuido_para') or None
            chamado.solucao = request.form.get('solucao', '')
            
            if chamado.status == 'resolvido' and not chamado.data_resolucao:
                chamado.data_resolucao = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Chamado atualizado com sucesso!', 'success')
            return redirect(url_for('chamado.visualizar', id=id))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar chamado!', 'danger')
    
    # Lista de equipamentos e técnicos
    equipamentos = Infraestrutura.query.filter_by(status='ativo').all()
    tecnicos = User.query.filter(User.role.in_(['admin', 'tech'])).all()
    
    return render_template('chamado_form.html',
                         chamado=chamado,
                         equipamentos=equipamentos,
                         tecnicos=tecnicos,
                         action='editar')

@chamado_bp.route('/<int:id>/deletar', methods=['POST'])
@login_required
def deletar(id):
    chamado = Chamado.query.get_or_404(id)
    
    # Apenas admin pode deletar
    if not current_user.is_admin:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('chamado.index'))
    
    try:
        db.session.delete(chamado)
        db.session.commit()
        flash('Chamado deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao deletar chamado!', 'danger')
    
    return redirect(url_for('chamado.index'))

@chamado_bp.route('/api/atribuir', methods=['POST'])
@login_required
def api_atribuir():
    """API para atribuir chamado a técnico"""
    if not current_user.is_tech:
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.get_json()
    chamado_id = data.get('chamado_id')
    tecnico_id = data.get('tecnico_id')
    
    chamado = Chamado.query.get(chamado_id)
    if not chamado:
        return jsonify({'error': 'Chamado não encontrado'}), 404
    
    chamado.atribuido_para = tecnico_id
    chamado.status = 'em_andamento'
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atribuir chamado'}), 500
