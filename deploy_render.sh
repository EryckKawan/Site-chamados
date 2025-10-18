#!/bin/bash
# Script para preparar deploy no Render

echo "🚀 Preparando Deploy para Render.com"
echo "===================================="

echo "✅ Arquivos necessários criados:"
echo "   - Procfile ✓"
echo "   - runtime.txt ✓"
echo "   - requirements.txt ✓"
echo ""

echo "📋 Passos para Deploy:"
echo ""
echo "1. Enviar código para GitHub:"
echo "   git add ."
echo "   git commit -m 'Preparar para deploy'"
echo "   git push origin main"
echo ""

echo "2. Acessar Render.com e fazer login"
echo ""

echo "3. New Web Service → Connect Repository"
echo ""

echo "4. Configurações:"
echo "   Name: chamados-ti"
echo "   Environment: Python 3"
echo "   Build Command: pip install -r requirements.txt"
echo "   Start Command: gunicorn app:app"
echo ""

echo "5. Environment Variables (opcional):"
echo "   SECRET_KEY = (gerar chave aleatória)"
echo ""

echo "6. Clicar em Create Web Service"
echo ""

echo "🎉 Seu app estará em: https://chamados-ti.onrender.com"
echo ""
echo "⏱️ Tempo estimado: 5-10 minutos"

