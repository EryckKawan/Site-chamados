# 🚀 Deploy com PostgreSQL no Render

## ✅ **Implementação Concluída!**

O sistema agora suporta **automaticamente**:
- 📁 **SQLite** - Para desenvolvimento local
- 🐘 **PostgreSQL** - Para produção no Render

---

## 📋 **Passo a Passo para Deploy**

### **1. Criar Banco PostgreSQL no Render**

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **"New +"** → **"PostgreSQL"**
3. Preencha:
   - **Name**: `chamados-ti-db`
   - **Database**: `chamados_ti`
   - **User**: `chamados_user`
   - **Region**: `Oregon (US West)` ou `Frankfurt (EU Central)`
   - **PostgreSQL Version**: `15` ou `16`
   - **Instance Type**: **Free**
4. Clique em **"Create Database"**
5. ⏳ Aguarde a criação (1-2 minutos)
6. **Copie** a **Internal Database URL**:
   ```
   postgresql://chamados_user:senha_gerada@dpg-xxxxx/chamados_ti
   ```

---

### **2. Configurar Web Service no Render**

#### **2.1. Criar ou Acessar Web Service**

Se ainda não criou:
1. Clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub
3. Escolha o repositório do projeto

#### **2.2. Configurações do Service**

- **Name**: `chamados-ti`
- **Region**: Mesma do banco (ex: `Oregon`)
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  gunicorn app:app
  ```

#### **2.3. Adicionar Variáveis de Ambiente**

Vá para **"Environment"** e adicione:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | (Cole a Internal Database URL copiada no passo 1) |
| `SECRET_KEY` | (Gere uma chave aleatória: `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `PYTHON_VERSION` | `3.11.0` |

**Exemplo de DATABASE_URL:**
```
postgresql://chamados_user:AbCd123XyZ@dpg-abc123-oregon.render.com/chamados_ti
```

#### **2.4. Deploy**

1. Clique em **"Create Web Service"** (ou **"Manual Deploy"** se já existir)
2. ⏳ Aguarde o deploy (3-5 minutos)
3. ✅ Acesse a URL gerada (ex: `https://chamados-ti.onrender.com`)

---

### **3. Inicializar o Banco de Dados**

Após o primeiro deploy, o banco estará vazio. Para criar as tabelas e usuário admin:

#### **Opção A: Via Shell do Render (Recomendado)**

1. No dashboard do **Web Service**, vá para **"Shell"**
2. Execute:
```bash
python database.py
```
3. Depois, crie o usuário admin:
```bash
python -c "from app import *; from werkzeug.security import generate_password_hash; conn = get_db_connection(); cursor = conn.cursor(); cursor.execute('INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING', ('Exponencial', 'exponencial@gmail.com', generate_password_hash('1234'), 'admin')); conn.commit(); conn.close(); print('✅ Usuário admin criado!')"
```

#### **Opção B: Criar rota temporária**

Adicione no `app.py` (REMOVER depois):
```python
@app.route('/setup-db')
def setup_db():
    if not USE_POSTGRES:
        return "Apenas para produção!"
    
    init_db()
    
    # Criar usuário admin
    from werkzeug.security import generate_password_hash
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        ''', ('Exponencial', 'exponencial@gmail.com', generate_password_hash('1234'), 'admin'))
        conn.commit()
        conn.close()
        return "✅ Banco inicializado e usuário admin criado!"
    except Exception as e:
        return f"❌ Erro: {e}"
```

Acesse: `https://seu-app.onrender.com/setup-db`

---

## 🔍 **Verificar se está funcionando**

### **1. Verificar logs:**
```bash
# No Render Dashboard → Logs
🐘 Usando PostgreSQL em produção
🔧 Criando tabelas no PostgreSQL...
✅ Banco de dados inicializado com sucesso!
🚀 Sistema de Chamados TI iniciado!
```

### **2. Testar login:**
```
URL: https://seu-app.onrender.com
Usuário: Exponencial
Senha: 1234
```

### **3. Criar novo usuário:**
Crie pelo sistema e **RECARREGUE A PÁGINA** → Usuário deve continuar lá!

---

## 🎯 **Diferenças entre Ambientes**

| Aspecto | Desenvolvimento (Local) | Produção (Render) |
|---------|-------------------------|-------------------|
| **Banco de Dados** | SQLite (`chamados_ti.db`) | PostgreSQL |
| **Detectado por** | Ausência de `DATABASE_URL` | Presença de `DATABASE_URL` |
| **Persistência** | Arquivo local | Servidor PostgreSQL |
| **Backup** | Manual (copiar `.db`) | Automático (Render) |
| **Performance** | Rápido (arquivo) | Muito rápido (servidor) |

---

## 📁 **Arquivos Modificados**

1. ✅ **`requirements.txt`** - Adicionado `psycopg2-binary`
2. ✅ **`database.py`** - Novo módulo (detecta ambiente automaticamente)
3. ✅ **`app.py`** - Usa `get_db_connection()` de `database.py`

---

## 🔄 **Como funciona a detecção automática**

```python
# Em database.py
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    # Usar PostgreSQL (produção)
    print("🐘 Usando PostgreSQL em produção")
else:
    # Usar SQLite (desenvolvimento)
    print("📁 Usando SQLite: chamados_ti.db")
```

**No seu computador:**
- `DATABASE_URL` não existe → Usa SQLite ✅

**No Render:**
- `DATABASE_URL` existe → Usa PostgreSQL ✅

---

## 🛠️ **Migrar Dados Existentes (Opcional)**

Se você já tem dados no SQLite e quer migrar para PostgreSQL:

### **1. Exportar dados do SQLite:**
```python
# export_data.py
import sqlite3
import json

conn = sqlite3.connect('chamados_ti.db')
conn.row_factory = sqlite3.Row

data = {}

# Exportar usuários
data['users'] = [dict(row) for row in conn.execute('SELECT * FROM users').fetchall()]

# Exportar funções
data['funcoes'] = [dict(row) for row in conn.execute('SELECT * FROM funcoes').fetchall()]

# Exportar chamados
data['chamados'] = [dict(row) for row in conn.execute('SELECT * FROM chamados').fetchall()]

with open('backup.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, default=str)

print("✅ Dados exportados para backup.json")
conn.close()
```

### **2. Importar no PostgreSQL:**
```python
# import_data.py
import json
import os
os.environ['DATABASE_URL'] = 'sua_url_postgresql_aqui'

from database import get_db_connection

with open('backup.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

conn = get_db_connection()
cursor = conn.cursor()

# Importar usuários
for user in data['users']:
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, funcao_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    ''', (user['username'], user['email'], user['password_hash'], user['role'], user.get('funcao_id')))

# ... (mesmo para funcoes, chamados, etc.)

conn.commit()
conn.close()
print("✅ Dados importados!")
```

---

## ⚠️ **Problemas Comuns**

### **1. Erro: "could not translate host name"**
- **Causa**: `DATABASE_URL` incorreta
- **Solução**: Verifique se copiou a URL completa

### **2. Erro: "No module named 'psycopg2'"**
- **Causa**: `psycopg2-binary` não instalado
- **Solução**: Verificar `requirements.txt` e fazer novo deploy

### **3. Tabelas não são criadas**
- **Causa**: `init_db()` não foi executado
- **Solução**: Executar via Shell ou rota `/setup-db`

### **4. Usuários não persistem**
- **Causa**: Ainda está usando SQLite em produção
- **Solução**: Verificar variável `DATABASE_URL` nas Environment Variables

---

## ✅ **Checklist de Deploy**

- [ ] PostgreSQL criado no Render
- [ ] `DATABASE_URL` copiada
- [ ] `requirements.txt` atualizado com `psycopg2-binary`
- [ ] Web Service configurado
- [ ] Variáveis de ambiente adicionadas (`DATABASE_URL`, `SECRET_KEY`)
- [ ] Deploy realizado com sucesso
- [ ] Logs mostram "🐘 Usando PostgreSQL em produção"
- [ ] Banco inicializado (`python database.py`)
- [ ] Usuário admin criado
- [ ] Login funciona
- [ ] Usuários persistem após reload

---

## 🎉 **Resultado Final**

✅ **SQLite** no desenvolvimento (rápido e simples)
✅ **PostgreSQL** em produção (seguro e persistente)
✅ **Detecção automática** de ambiente
✅ **Nunca mais perde usuários** nos deploys!
✅ **Código único** para ambos os ambientes

**🚀 Agora você tem um sistema profissional e robusto!**

