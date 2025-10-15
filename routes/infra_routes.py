from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.infraestrutura import Infraestrutura
from models.chamado import Chamado
from models import db
from datetime import datetime

infra_bp = Blueprint('infra', __name__)

@infra_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    tipo_filter = request.args.get('tipo', '')
    status_filter = request.args.get('status', '')
    localizacao_filter = request.args.get('localizacao', '')
    
    query = Infraestrutura.query
    
    # Filtros
    if tipo_filter:
        query = query.filter_by(tipo=tipo_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if localizacao_filter:
        query = query.filter(Infraestrutura.localizacao.contains(localizacao_filter))
    
    equipamentos = query.order_by(Infraestrutura.nome).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Listas para filtros
    tipos = db.session.query(Infraestrutura.tipo).distinct().all()
    tipos = [tipo[0] for tipo in tipos]
    
    localizacoes = db.session.query(Infraestrutura.localizacao).distinct().all()
    localizacoes = [loc[0] for loc in localizacoes]
    
    return render_template('infraestrutura.html',
                         equipamentos=equipamentos,
                         tipos=tipos,
                         localizacoes=localizacoes,
                         tipo_filter=tipo_filter,
                         status_filter=status_filter,
                         localizacao_filter=localizacao_filter)

@infra_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if not current_user.is_tech:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('infra.index'))
    
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
        
        # Converter data
        data_aquisicao_obj = None
        if data_aquisicao:
            try:
                data_aquisicao_obj = datetime.strptime(data_aquisicao, '%Y-%m-%d').date()
            except ValueError:
                flash('Data de aquisição inválida!', 'danger')
                return render_template('infra_form.html', action='novo')
        
        equipamento = Infraestrutura(
            nome=nome,
            tipo=tipo,
            marca=marca,
            modelo=modelo,
            numero_serie=numero_serie,
            localizacao=localizacao,
            responsavel=responsavel,
            status=status,
            data_aquisicao=data_aquisicao_obj,
            observacoes=observacoes
        )
        
        try:
            db.session.add(equipamento)
            db.session.commit()
            flash('Equipamento cadastrado com sucesso!', 'success')
            return redirect(url_for('infra.index'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar equipamento!', 'danger')
    
    return render_template('infra_form.html', action='novo')

@infra_bp.route('/<int:id>')
@login_required
def visualizar(id):
    equipamento = Infraestrutura.query.get_or_404(id)
    
    # Buscar chamados relacionados
    chamados = Chamado.query.filter_by(equipamento_id=id).order_by(
        Chamado.data_criacao.desc()
    ).limit(10).all()
    
    return render_template('infra_detalhes.html',
                         equipamento=equipamento,
                         chamados=chamados)

@infra_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not current_user.is_tech:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('infra.index'))
    
    equipamento = Infraestrutura.query.get_or_404(id)
    
    if request.method == 'POST':
        equipamento.nome = request.form['nome']
        equipamento.tipo = request.form['tipo']
        equipamento.marca = request.form.get('marca', '')
        equipamento.modelo = request.form.get('modelo', '')
        equipamento.numero_serie = request.form.get('numero_serie', '')
        equipamento.localizacao = request.form['localizacao']
        equipamento.responsavel = request.form.get('responsavel', '')
        equipamento.status = request.form['status']
        equipamento.observacoes = request.form.get('observacoes', '')
        
        # Atualizar data de aquisição
        data_aquisicao = request.form.get('data_aquisicao')
        if data_aquisicao:
            try:
                equipamento.data_aquisicao = datetime.strptime(data_aquisicao, '%Y-%m-%d').date()
            except ValueError:
                flash('Data de aquisição inválida!', 'danger')
                return render_template('infra_form.html', equipamento=equipamento, action='editar')
        
        try:
            db.session.commit()
            flash('Equipamento atualizado com sucesso!', 'success')
            return redirect(url_for('infra.visualizar', id=id))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar equipamento!', 'danger')
    
    return render_template('infra_form.html',
                         equipamento=equipamento,
                         action='editar')

@infra_bp.route('/<int:id>/deletar', methods=['POST'])
@login_required
def deletar(id):
    if not current_user.is_admin:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('infra.index'))
    
    equipamento = Infraestrutura.query.get_or_404(id)
    
    # Verificar se há chamados associados
    chamados_count = Chamado.query.filter_by(equipamento_id=id).count()
    if chamados_count > 0:
        flash(f'Não é possível deletar equipamento com {chamados_count} chamado(s) associado(s)!', 'danger')
        return redirect(url_for('infra.visualizar', id=id))
    
    try:
        db.session.delete(equipamento)
        db.session.commit()
        flash('Equipamento deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao deletar equipamento!', 'danger')
    
    return redirect(url_for('infra.index'))

@infra_bp.route('/api/status', methods=['POST'])
@login_required
def api_status():
    """API para alterar status do equipamento"""
    if not current_user.is_tech:
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.get_json()
    equipamento_id = data.get('equipamento_id')
    novo_status = data.get('status')
    
    equipamento = Infraestrutura.query.get(equipamento_id)
    if not equipamento:
        return jsonify({'error': 'Equipamento não encontrado'}), 404
    
    equipamento.status = novo_status
    if novo_status == 'manutencao':
        equipamento.data_ultima_manutencao = datetime.utcnow().date()
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar status'}), 500
