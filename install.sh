#!/bin/bash

echo "========================================"
echo "  Sistema de Chamados TI - Instalação"
echo "========================================"
echo

echo "[1/4] Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar ambiente virtual"
    exit 1
fi

echo "[2/4] Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao ativar ambiente virtual"
    exit 1
fi

echo "[3/4] Instalando dependências..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências"
    exit 1
fi

echo "[4/4] Inicializando banco de dados..."
python run.py --sample
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao inicializar banco de dados"
    exit 1
fi

echo
echo "========================================"
echo "  Instalação concluída com sucesso!"
echo "========================================"
echo
echo "Para executar o sistema:"
echo "  1. Ative o ambiente virtual: source venv/bin/activate"
echo "  2. Execute: python run.py"
echo "  3. Acesse: http://127.0.0.1:5000"
echo
echo "Login padrão: admin / admin123"
echo

