#!/bin/bash
# Script de deploy para PythonAnywhere

echo "🚀 Deploy para PythonAnywhere"
echo "================================"

# Variáveis (AJUSTE CONFORME NECESSÁRIO)
PA_USER="seu_usuario"
PA_DOMAIN="${PA_USER}.pythonanywhere.com"

echo "📦 1. Fazendo zip do projeto..."
zip -r chamados_ti.zip . -x "*.git*" "venv/*" "*.pyc" "__pycache__/*"

echo "📤 2. Faça upload manual do arquivo chamados_ti.zip para PythonAnywhere"
echo "   URL: https://www.pythonanywhere.com/user/${PA_USER}/files/"

echo ""
echo "🔧 3. No console Bash do PythonAnywhere, execute:"
echo ""
echo "   unzip chamados_ti.zip -d ~/TI"
echo "   cd ~/TI"
echo "   mkvirtualenv --python=/usr/bin/python3.10 venv"
echo "   pip install -r requirements.txt"
echo ""

echo "🌐 4. Configurar Web App:"
echo "   - Dashboard → Web → Add new web app"
echo "   - Source code: /home/${PA_USER}/TI"
echo "   - Working directory: /home/${PA_USER}/TI"
echo "   - Virtualenv: /home/${PA_USER}/.virtualenvs/venv"
echo ""

echo "📝 5. Editar WSGI file e adicionar:"
echo ""
echo "   import sys"
echo "   path = '/home/${PA_USER}/TI'"
echo "   if path not in sys.path:"
echo "       sys.path.append(path)"
echo "   from app import app as application"
echo ""

echo "✅ 6. Clique em Reload no topo da página"
echo ""
echo "🎉 Seu site estará em: https://${PA_DOMAIN}"

