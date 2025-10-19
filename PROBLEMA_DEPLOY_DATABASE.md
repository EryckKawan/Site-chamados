# ⚠️ Por que você perde os usuários a cada deploy?

## 🔍 **Problema Identificado:**

Você está usando **SQLite** (`database.db`) e o arquivo está sendo **ignorado pelo Git** (`.gitignore`):

```gitignore
# Banco de Dados
*.db                  # ❌ Ignora TODOS os arquivos .db
!chamados_ti.db       # ✅ EXCETO chamados_ti.db
```

### **O que acontece no deploy:**

1. Você faz deploy no **Render** (ou outro serviço)
2. O serviço **clona apenas o código do Git**
3. O arquivo `database.db` **NÃO está no Git** (ignorado)
4. O sistema **cria um novo banco vazio**
5. **Todos os usuários são perdidos** ❌

---

## ✅ **Soluções Disponíveis:**

### **Solução 1: Usar PostgreSQL (RECOMENDADO para produção)** 🐘

O Render oferece PostgreSQL **gratuito** e os dados são **persistentes**.

#### **Vantagens:**
- ✅ Dados **nunca são perdidos**
- ✅ **Mais rápido** que SQLite
- ✅ **Mais seguro**
- ✅ Suporta **múltiplos usuários simultâneos**
- ✅ **Backups automáticos**

#### **Como implementar:**

1. **Instalar dependência:**
```bash
pip install psycopg2-binary
```

2. **Atualizar `requirements.txt`:**
```txt
Flask==2.3.0
Flask-Login==0.6.2
psycopg2-binary==2.9.9
```

3. **Modificar `app.py`:**
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# Detectar ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Produção (Render) - PostgreSQL
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
else:
    # Desenvolvimento - SQLite
    engine = create_engine('sqlite:///database.db')
```

4. **No Render:**
   - Criar um **PostgreSQL database**
   - Copiar a **DATABASE_URL**
   - Adicionar nas **Environment Variables**

---

### **Solução 2: Commitar o banco de dados (TEMPORÁRIO)** 📦

**⚠️ NÃO RECOMENDADO para produção!**

#### **Passos:**

1. **Modificar `.gitignore`:**
```gitignore
# Banco de Dados
# *.db                  # ❌ COMENTAR esta linha
!database.db            # ✅ Permitir database.db
*_backup_*.db
backup_*.db
```

2. **Adicionar ao Git:**
```bash
git add database.db
git commit -m "feat: Adicionar database.db para persistência"
git push
```

#### **Desvantagens:**
- ❌ Dados de produção no repositório (inseguro)
- ❌ Conflitos ao fazer deploy
- ❌ Tamanho do repositório cresce
- ❌ Não funciona com múltiplos servidores

---

### **Solução 3: Volume Persistente (Render Disk)** 💾

O Render oferece **discos persistentes** (pagos).

#### **Como funcionar:**

1. **No Render Dashboard:**
   - Criar um **Persistent Disk**
   - Montar em `/opt/render/project/src/data`

2. **Modificar `app.py`:**
```python
import os

# Diretório de dados persistentes
DATA_DIR = os.environ.get('DATA_DIR', '.')
DATABASE_PATH = os.path.join(DATA_DIR, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

3. **Adicionar variável de ambiente:**
```
DATA_DIR=/opt/render/project/src/data
```

#### **Desvantagens:**
- ❌ **Pago** (não disponível no plano gratuito)
- ❌ Ainda usa SQLite (limitações)

---

### **Solução 4: Banco de Dados Externo** ☁️

Usar serviços como **Supabase**, **PlanetScale**, **Railway**, etc.

#### **Vantagens:**
- ✅ **Gratuito** (planos free)
- ✅ Dados **persistentes**
- ✅ **PostgreSQL** ou **MySQL**
- ✅ Interface web para gerenciar

---

## 🎯 **Recomendação: PostgreSQL no Render**

### **Por que PostgreSQL?**

| Critério | SQLite | PostgreSQL |
|----------|--------|------------|
| **Persistência** | ❌ Perdido a cada deploy | ✅ Sempre persistente |
| **Performance** | ⚠️ Limitado | ✅ Excelente |
| **Múltiplos usuários** | ❌ Problemas | ✅ Suporta |
| **Backups** | ❌ Manual | ✅ Automático |
| **Produção** | ❌ Não recomendado | ✅ Ideal |
| **Custo no Render** | Gratuito | Gratuito |

---

## 📋 **Passo a Passo: Migrar para PostgreSQL**

### **1. Criar PostgreSQL no Render:**

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **"New +"** → **"PostgreSQL"**
3. Escolha:
   - **Name**: `chamados-ti-db`
   - **Database**: `chamados_ti`
   - **User**: `chamados_user`
   - **Region**: `Oregon (US West)`
   - **PostgreSQL Version**: `15`
   - **Instance Type**: `Free`
4. Clique em **"Create Database"**
5. Copie a **Internal Database URL** (formato: `postgresql://...`)

### **2. Adicionar variável de ambiente:**

1. Vá para seu **Web Service** no Render
2. **Environment** → **Add Environment Variable**
3. Adicione:
   - **Key**: `DATABASE_URL`
   - **Value**: (cole a URL copiada)

### **3. Atualizar código:**

Vou criar o código completo para você!

---

## 🔒 **Segurança:**

### **❌ NUNCA fazer:**
- Commitar senhas no código
- Commitar banco de dados com dados reais
- Usar SQLite em produção com múltiplos usuários

### **✅ SEMPRE fazer:**
- Usar variáveis de ambiente para credenciais
- Usar PostgreSQL em produção
- Fazer backups regulares
- Usar `.gitignore` para dados sensíveis

---

## 🆘 **Situação Atual:**

```
Local (desenvolvimento):
✅ SQLite (database.db) - FUNCIONA
   Usuários são salvos localmente

Deploy (Render):
❌ SQLite (database.db) - NÃO FUNCIONA
   Banco não está no Git
   Cada deploy = banco novo vazio
   Todos os usuários são perdidos
```

## 🎯 **Solução Final:**

```
Local (desenvolvimento):
✅ SQLite (database.db) - Para desenvolvimento

Deploy (Render):
✅ PostgreSQL - Para produção
   Dados são persistentes
   Nunca perde usuários
   Performance melhor
```

---

**Qual solução você prefere implementar?**

1. **PostgreSQL no Render** (RECOMENDADO) 🐘
2. **Commitar database.db temporariamente** 📦
3. **Volume persistente** (pago) 💾
4. **Banco externo** (Supabase/Railway) ☁️

**Posso te ajudar a implementar qualquer uma delas!** 🚀

