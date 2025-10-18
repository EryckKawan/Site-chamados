# 🚀 Guia de Deploy - Colocar o Sistema Online

## Opções de Hospedagem

### 🌟 Opção 1: PythonAnywhere (GRÁTIS e Fácil)

**Melhor para:** Começar rapidamente, teste, projetos pequenos

#### Passos:

1. **Criar conta em** https://www.pythonanywhere.com
2. **Plano gratuito** permite 1 aplicação web
3. **Upload dos arquivos:**
   - Use o terminal bash ou upload de arquivos
   - Envie todos os arquivos do projeto
4. **Configurar Web App:**
   - Dashboard → Web → Add a new web app
   - Escolha: Flask
   - Python 3.10+
   - Caminho para app.py: `/home/seuusuario/TI/app.py`
5. **Instalar dependências:**
   ```bash
   pip install --user -r requirements.txt
   ```
6. **Configurar WSGI:**
   ```python
   import sys
   path = '/home/seuusuario/TI'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```
7. **Reload** e pronto!

**URL:** `seuusuario.pythonanywhere.com`

---

### 🔥 Opção 2: Heroku (Fácil, Pago)

**Melhor para:** Escalabilidade, banco PostgreSQL

#### Passos:

1. **Criar conta em** https://www.heroku.com
2. **Instalar Heroku CLI**
3. **Criar arquivos necessários:**

**Procfile:**
```
web: gunicorn app:app
```

**runtime.txt:**
```
python-3.11.0
```

**requirements.txt** (adicionar):
```
gunicorn==21.2.0
psycopg2-binary==2.9.9  # Para PostgreSQL
```

4. **Deploy:**
```bash
heroku login
heroku create nome-do-seu-app
git push heroku main
heroku open
```

**URL:** `nome-do-seu-app.herokuapp.com`

---

### 🐳 Opção 3: Render (Grátis com limitações)

**Melhor para:** Deploy automático via GitHub

#### Passos:

1. **Enviar código para GitHub**
2. **Criar conta em** https://render.com
3. **New Web Service** → Conectar GitHub
4. **Configurações:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. **Deploy automático!**

**URL:** `nome-do-app.onrender.com`

---

### 💻 Opção 4: VPS/Servidor Próprio (Controle Total)

**Melhor para:** Produção séria, controle total

#### Recomendado: Ubuntu Server na DigitalOcean, AWS, Azure

#### Passos Completos:

**1. Preparar Servidor (Ubuntu 22.04):**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3.10 python3-pip python3-venv nginx supervisor -y

# Criar usuário para app
sudo useradd -m -s /bin/bash appuser
sudo su - appuser
```

**2. Upload do Projeto:**

```bash
# Clonar ou fazer upload dos arquivos
cd /home/appuser
git clone seu-repositorio.git TI
cd TI

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn
```

**3. Criar arquivo de configuração Gunicorn:**

**`gunicorn_config.py`:**
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
accesslog = "/home/appuser/TI/logs/access.log"
errorlog = "/home/appuser/TI/logs/error.log"
loglevel = "info"
```

**4. Configurar Supervisor (manter app rodando):**

**`/etc/supervisor/conf.d/chamados_ti.conf`:**
```ini
[program:chamados_ti]
directory=/home/appuser/TI
command=/home/appuser/TI/venv/bin/gunicorn -c gunicorn_config.py app:app
user=appuser
autostart=true
autorestart=true
stderr_logfile=/var/log/chamados_ti.err.log
stdout_logfile=/var/log/chamados_ti.out.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start chamados_ti
```

**5. Configurar Nginx (servidor web):**

**`/etc/nginx/sites-available/chamados_ti`:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/appuser/TI/static;
        expires 30d;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/chamados_ti /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**6. SSL (HTTPS) com Let's Encrypt:**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu-dominio.com
```

---

### 🔒 **Segurança para Produção**

**Atualize `app.py` para produção:**

```python
# Trocar SECRET_KEY por uma chave aleatória forte
import secrets
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Gerar uma vez e guardar

# Desativar debug em produção
if __name__ == '__main__':
    app.run(debug=False)  # IMPORTANTE!
```

**Criar arquivo `.env` para configurações:**

```bash
SECRET_KEY=sua-chave-super-secreta-aqui
DATABASE_URL=sqlite:///chamados_ti.db
FLASK_ENV=production
```

---

### 📊 **Banco de Dados para Produção**

**Migrar de SQLite para PostgreSQL (recomendado):**

1. **Instalar PostgreSQL:**
```bash
sudo apt install postgresql postgresql-contrib
```

2. **Criar banco:**
```bash
sudo -u postgres psql
CREATE DATABASE chamados_ti;
CREATE USER appuser WITH PASSWORD 'senha-forte';
GRANT ALL PRIVILEGES ON DATABASE chamados_ti TO appuser;
\q
```

3. **Atualizar app.py:**
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://appuser:senha@localhost/chamados_ti'
```

---

### 🎨 **Domínio Personalizado**

**Opções:**

1. **Comprar domínio:** Registro.br, GoDaddy, Namecheap
2. **Apontar para seu servidor:**
   - Tipo A: IP do servidor
   - Aguardar propagação DNS (até 48h)
3. **Configurar SSL** com Let's Encrypt

---

### ⚡ **Performance e Otimização**

1. **Use Gunicorn em produção:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Cache com Redis:**
   ```bash
   pip install redis flask-caching
   ```

3. **CDN para arquivos estáticos:**
   - Cloudflare (grátis)
   - AWS CloudFront

---

### 📦 **Checklist de Deploy**

- [ ] Código no GitHub/GitLab
- [ ] Secret key forte e segura
- [ ] Debug = False em produção
- [ ] Banco de dados configurado
- [ ] Gunicorn instalado
- [ ] Nginx configurado
- [ ] SSL/HTTPS ativo
- [ ] Backup automático do banco
- [ ] Logs configurados
- [ ] Firewall configurado (porta 80, 443)
- [ ] Domínio apontando para servidor

---

### 🆘 **Problemas Comuns**

**Erro 502 Bad Gateway:**
- Verificar se Gunicorn está rodando: `sudo supervisorctl status`
- Ver logs: `sudo tail -f /var/log/chamados_ti.err.log`

**Erro de permissão:**
- Verificar dono dos arquivos: `sudo chown -R appuser:appuser /home/appuser/TI`

**Banco não atualiza:**
- Migrar dados do SQLite para produção
- Recriar tabelas com `init_db()`

---

### 💰 **Custos Estimados**

| Serviço | Custo Mensal | Características |
|---------|--------------|-----------------|
| PythonAnywhere | **R$ 0** | Grátis, limitado |
| Render | **R$ 0-37** | Grátis com sono, pago sem |
| Heroku | **R$ 37+** | Fácil, escalável |
| DigitalOcean | **R$ 24+** | VPS, controle total |
| AWS EC2 | **R$ 50+** | Profissional |

---

### 🎯 **Recomendação**

Para **começar:**
1. **PythonAnywhere** (grátis) ou **Render** (grátis com limitações)

Para **produção séria:**
1. **VPS (DigitalOcean)** + Nginx + Gunicorn + PostgreSQL
2. Backup automático diário
3. Monitoramento (Uptime Robot grátis)

---

### 📚 **Próximos Passos**

1. Escolher plataforma de hospedagem
2. Seguir guia específico acima
3. Testar completamente em produção
4. Configurar backups
5. Monitorar e ajustar conforme necessário

**Quer que eu crie scripts de deploy automatizado para alguma dessas plataformas?** 🚀

