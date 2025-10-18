# ⚡ Deploy Rápido - 3 Opções Simples

## 🌟 Opção 1: PythonAnywhere (Mais Fácil - GRÁTIS)

### ⏱️ Tempo: ~15 minutos

1. Criar conta: https://www.pythonanywhere.com
2. Upload dos arquivos via Dashboard
3. Executar no console bash:
   ```bash
   cd ~/TI
   mkvirtualenv --python=python3.10 venv
   pip install -r requirements.txt
   ```
4. Configurar Web App → Flask → Python 3.10
5. Editar WSGI file, adicionar:
   ```python
   import sys
   sys.path.append('/home/seuusuario/TI')
   from app import app as application
   ```
6. Reload → Pronto!

**URL:** `seuusuario.pythonanywhere.com`

---

## 🔥 Opção 2: Render (Deploy Automático - GRÁTIS*)

### ⏱️ Tempo: ~10 minutos

**Pré-requisito:** Código no GitHub

1. Acesse https://render.com e faça login
2. **New** → **Web Service**
3. Conecte seu repositório GitHub
4. Configurações:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:app`
5. **Create Web Service**
6. Aguarde build (~5 min)

**URL:** `nome-do-app.onrender.com`

*Plano grátis "dorme" após 15min de inatividade

---

## 🚀 Opção 3: Heroku (Profissional - PAGO)

### ⏱️ Tempo: ~10 minutos

**Pré-requisito:** Conta Heroku + CLI instalado

```bash
# Login
heroku login

# Criar app
heroku create nome-do-seu-app

# Deploy
git push heroku main

# Abrir
heroku open
```

**URL:** `nome-do-seu-app.herokuapp.com`

**Custo:** ~$7/mês (plano básico)

---

## 📋 Arquivos Já Criados Para Você

- ✅ `Procfile` - Config para Heroku/Render
- ✅ `runtime.txt` - Versão do Python
- ✅ `requirements.txt` - Dependências (com gunicorn)
- ✅ `wsgi.py` - Entry point WSGI
- ✅ `config_production.py` - Configurações de produção

---

## ⚡ Deploy em 3 Comandos (Render)

```bash
# 1. Push para GitHub
git push origin main

# 2. Conectar no Render.com via interface web

# 3. Aguardar build automático
# Pronto! ✅
```

---

## 🔒 Checklist de Segurança

Antes de colocar online:

- [ ] Trocar `SECRET_KEY` por valor seguro
- [ ] Desativar `DEBUG = False` em produção
- [ ] Usar senha forte para admin
- [ ] Configurar HTTPS
- [ ] Fazer backup do banco de dados

---

## 💡 Dica Pro

**Melhor escolha para começar:**
1. **Teste:** PythonAnywhere (grátis)
2. **Produção pequena:** Render (grátis com sono)
3. **Produção séria:** VPS próprio (DigitalOcean $6/mês)

---

## 🆘 Precisa de Ajuda?

- 📚 Guia completo: `DEPLOY_GUIA.md`
- 🔧 Scripts prontos: `deploy_*.sh`
- 📖 Documentação oficial de cada plataforma

**Escolha uma opção e siga o guia!** 🚀

