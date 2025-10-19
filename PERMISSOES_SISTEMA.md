# 🔐 Sistema de Permissões

## Níveis de Acesso

### 👑 **Administrador** (`admin`)
**Acesso Total ao Sistema**
- ✅ Dashboard
- ✅ Chamados (todos)
- ✅ Infraestrutura
- ✅ Armazenamento de Servidores
- ✅ Funções/Cargos
- ✅ Configurações
- ✅ Gerenciar Usuários
- ✅ Chat

### 👨‍💼 **Diretor** (`diretor`)
**Visão Completa Operacional**
- ✅ Dashboard
- ✅ Chamados (todos)
- ✅ Infraestrutura
- ✅ Armazenamento de Servidores
- ✅ Chat
- ❌ Funções/Cargos (apenas admin)
- ❌ Configurações (apenas admin)

### 👨‍🏫 **Supervisor** (`supervisor`)
**Gestão Técnica Completa**
- ✅ Dashboard
- ✅ Chamados (todos)
- ✅ Infraestrutura
- ✅ Armazenamento de Servidores
- ✅ Chat
- ❌ Funções/Cargos (apenas admin)
- ❌ Configurações (apenas admin)

### 🔧 **Técnico** (`tech`)
**Suporte Técnico**
- ✅ Dashboard
- ✅ Chamados (todos)
- ✅ Infraestrutura
- ✅ Armazenamento de Servidores
- ✅ Chat
- ❌ Funções/Cargos (apenas admin)
- ❌ Configurações (apenas admin)

### 📋 **Administrativo** (`administrativo`)
**Gestão de Chamados**
- ✅ Dashboard
- ✅ Chamados (todos)
- ✅ Chat
- ❌ Infraestrutura
- ❌ Armazenamento de Servidores
- ❌ Funções/Cargos
- ❌ Configurações

### 👤 **Usuário** (`user`)
**Acesso Básico**
- ✅ Dashboard
- ✅ Chamados (apenas os próprios)
- ❌ Infraestrutura
- ❌ Armazenamento
- ❌ Funções/Cargos
- ❌ Configurações
- ❌ Chat

---

## Funções de Verificação

### `is_admin()`
Retorna `True` apenas para administradores

### `is_tech()`
Retorna `True` para: admin, diretor, supervisor, tech

### `is_administrativo()`
Retorna `True` apenas para administrativo

### `can_access_chamados()`
Retorna `True` para: todos (admin, diretor, supervisor, tech, administrativo, user)

### `can_access_infraestrutura()`
Retorna `True` para: admin, diretor, supervisor, tech

### `can_access_storage()`
Retorna `True` para: admin, diretor, supervisor, tech

### `can_access_funcoes()`
Retorna `True` para: admin

### `can_access_configuracoes()`
Retorna `True` para: admin

### `can_access_chat()`
Retorna `True` para: admin, diretor, supervisor, tech, administrativo

---

## Como Alterar a Role de um Usuário

### Via Painel Admin:
1. Login como admin
2. Acesse: Configurações → Gerenciar Usuários
3. Clique em "Editar" no usuário desejado
4. Selecione a nova função
5. Salve

### Via SQL Direto:
```sql
UPDATE users SET role = 'diretor' WHERE username = 'fulano';
```

Opções válidas: `admin`, `diretor`, `supervisor`, `tech`, `administrativo`, `user`

---

## Labels Personalizáveis

As labels das roles são armazenadas na tabela `role_names` e podem ser customizadas:

| role_key | label (padrão) |
|----------|----------------|
| admin | Administrador |
| diretor | Diretor |
| supervisor | Supervisor |
| tech | Técnico |
| administrativo | Administrativo |
| user | Usuário |

---

## Resumo de Permissões por Módulo

| Módulo | Admin | Diretor | Supervisor | Técnico | Administrativo | Usuário |
|--------|-------|---------|------------|---------|----------------|---------|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Chamados | ✅ Todos | ✅ Todos | ✅ Todos | ✅ Todos | ✅ Todos | ✅ Próprios |
| Infraestrutura | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Armazenamento | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Funções | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Configurações | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Chat | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

---

**Última atualização:** 2025-01-19

