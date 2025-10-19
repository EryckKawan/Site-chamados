# 🔐 Sistema de Permissões Granulares

## 📋 Visão Geral

O sistema agora possui **permissões granulares** que permitem controlar individualmente cada funcionalidade que um usuário pode acessar.

## 🎯 Como Funciona

### ✨ Interface Visual com Botões Toggle

Na tela de **Editar Usuário**, você encontrará uma seção completa de **Permissões de Acesso** com botões interativos:

- ✅ **Botão Verde "Permitido"** - Permissão ativada
- ❌ **Botão Vermelho "Negado"** - Permissão desativada

**Clique nos botões para alternar** entre permitir ou negar cada permissão!

## 🔑 Permissões Disponíveis

### 1. 📋 Visualizar Chamados
- **Descrição**: Ver todos os chamados do sistema
- **Chave**: `view_chamados`
- **Uso**: Permite visualizar a lista completa de chamados

### 2. ➕ Criar Chamados
- **Descrição**: Abrir novos chamados
- **Chave**: `create_chamados`
- **Uso**: Permite criar chamados no sistema

### 3. ✏️ Editar Chamados
- **Descrição**: Modificar chamados existentes
- **Chave**: `edit_chamados`
- **Uso**: Permite editar informações de chamados

### 4. 🗑️ Deletar Chamados
- **Descrição**: Excluir chamados do sistema
- **Chave**: `delete_chamados`
- **Uso**: Permite remover chamados permanentemente

### 5. 👤 Atribuir Chamados
- **Descrição**: Designar chamados para técnicos
- **Chave**: `assign_chamados`
- **Uso**: Permite atribuir chamados a outros usuários

### 6. 💻 Gerenciar Equipamentos
- **Descrição**: Acessar infraestrutura
- **Chave**: `manage_infrastructure`
- **Uso**: Permite gerenciar equipamentos e infraestrutura

### 7. 👥 Gerenciar Usuários
- **Descrição**: Criar/editar usuários
- **Chave**: `manage_users`
- **Uso**: Permite administrar usuários do sistema

### 8. 💬 Acessar Chat
- **Descrição**: Chat de suporte
- **Chave**: `access_chat`
- **Uso**: Permite acessar o sistema de chat

## 🛠️ Como Configurar Permissões

### Passo 1: Acessar Gestão de Usuários
1. Faça login como **Administrador**
2. Acesse o menu lateral → **Usuários**

### Passo 2: Editar Usuário
1. Clique no botão **Editar** do usuário desejado
2. Role a página até a seção **Permissões de Acesso**

### Passo 3: Configurar Permissões
1. **Clique nos botões** para alternar entre:
   - ✅ **Permitido** (verde)
   - ❌ **Negado** (vermelho)
2. O card muda de cor conforme o status:
   - **Verde claro** = Permissão ativada
   - **Vermelho claro** = Permissão desativada

### Passo 4: Salvar
1. Clique em **Salvar Alterações**
2. As permissões serão salvas no banco de dados

## 💾 Estrutura do Banco de Dados

### Tabela: `user_permissions`

```sql
CREATE TABLE user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    permission_key TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    UNIQUE(user_id, permission_key),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
```

## 🔧 Uso em Código

### Verificar Permissão em Rotas Python

```python
from app import has_permission

@app.route('/alguma-rota')
@login_required
def alguma_funcao():
    if not has_permission('view_chamados'):
        flash('Você não tem permissão para visualizar chamados', 'danger')
        return redirect(url_for('dashboard'))
    
    # Continuar com a lógica...
```

### Verificar Permissão em Templates

```html
{% if has_permission('delete_chamados') %}
    <button class="btn btn-danger">Deletar</button>
{% endif %}
```

## 📊 Funcionalidades Implementadas

### ✅ Frontend
- [x] Interface visual com cards coloridos
- [x] Botões toggle interativos (✅ Permitido / ❌ Negado)
- [x] Animações e feedback visual
- [x] Mudança de cor dos cards conforme status
- [x] Carregamento automático das permissões salvas

### ✅ Backend
- [x] Tabela de permissões no banco de dados
- [x] Salvamento de permissões na edição de usuário
- [x] Funções helper: `has_permission()`, `get_user_permissions()`
- [x] Injeção de funções nos templates
- [x] Admin sempre tem todas as permissões

### ✅ Segurança
- [x] Apenas admin pode editar permissões
- [x] Validação no backend
- [x] Proteção contra SQL injection
- [x] Cascata de deleção (se usuário for deletado, permissões também)

## 🎨 Características Visuais

### Botões Toggle
- **Verde** (`#28a745`): Permissão ativada
- **Vermelho** (`#dc3545`): Permissão desativada
- **Hover**: Aumenta de tamanho (scale 1.05)
- **Click**: Animação de "aperto" (scale 0.95)

### Cards de Permissão
- **Borda verde**: Quando permissão está ativa
- **Fundo verde claro** (`#f8fff9`): Permissão ativa
- **Borda vermelha**: Quando permissão está desativada
- **Fundo vermelho claro** (`#fff8f8`): Permissão desativada
- **Sombra no hover**: Destaque visual

## 📝 Exemplos de Uso

### Exemplo 1: Usuário Básico
```
✅ Visualizar Chamados
✅ Criar Chamados
❌ Editar Chamados
❌ Deletar Chamados
❌ Atribuir Chamados
❌ Gerenciar Equipamentos
❌ Gerenciar Usuários
✅ Acessar Chat
```

### Exemplo 2: Técnico
```
✅ Visualizar Chamados
✅ Criar Chamados
✅ Editar Chamados
❌ Deletar Chamados
✅ Atribuir Chamados
✅ Gerenciar Equipamentos
❌ Gerenciar Usuários
✅ Acessar Chat
```

### Exemplo 3: Administrador
```
✅ TODAS AS PERMISSÕES (sempre)
```

## 🚀 Próximos Passos

Para expandir o sistema de permissões:

1. **Adicionar mais permissões** conforme necessário
2. **Criar perfis de permissão** (templates pré-configurados)
3. **Adicionar auditoria** (log de mudanças de permissões)
4. **Implementar permissões em nível de objeto** (ex: editar apenas seus próprios chamados)

---

**Desenvolvido com ❤️ para controle granular de acesso**

