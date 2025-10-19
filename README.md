# Sistema de Chamados TI

Sistema completo de gerenciamento de chamados de TI com interface moderna e funcionalidades avançadas.

## 🚀 Funcionalidades

### 👥 Gestão de Usuários
- Sistema de autenticação com Flask-Login
- Diferentes níveis de acesso (Admin, Técnico, Usuário)
- Cadastro e login de usuários
- Usuário admin padrão: `admin` / `admin123`

### 🎫 Gerenciamento de Chamados
- Criação, edição e visualização de chamados
- Sistema de prioridades (Baixa, Média, Alta, Crítica)
- Categorização por tipo (Hardware, Software, Rede, Email, etc.)
- Status de acompanhamento (Aberto, Em Andamento, Resolvido, Fechado)
- Atribuição de chamados para técnicos
- Filtros avançados e paginação
- Histórico completo de alterações

### 🖥️ Infraestrutura
- Cadastro e gerenciamento de equipamentos
- Controle de localização e responsáveis
- Status de equipamentos (Ativo, Inativo, Manutenção)
- Histórico de manutenções
- Relacionamento com chamados

### 📊 Dashboard Inteligente
- Estatísticas em tempo real
- Gráficos de prioridades e categorias
- Chamados recentes e atribuídos
- Equipamentos com mais problemas
- Ações rápidas

### 💬 Chat de Suporte (Preparado)
- Endpoint `/api/chat` para integração futura com OpenAI
- Respostas automáticas para perguntas comuns
- Interface de chat integrada

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Chart.js, Bootstrap Icons
- **Database**: SQLite (desenvolvimento)
- **Design**: Interface responsiva com tema corporativo

## 📁 Estrutura do Projeto

```
TI/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências
├── README.md             # Documentação
├── models/               # Modelos de dados
│   ├── __init__.py
│   ├── user.py
│   ├── chamado.py
│   ├── infraestrutura.py
│   └── funcao.py
├── routes/               # Blueprints de rotas
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── chamado_routes.py
│   ├── infra_routes.py
│   ├── funcao_routes.py
│   └── dashboard_routes.py
├── templates/            # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── chamados.html
│   ├── chamado_form.html
│   ├── chamado_detalhes.html
│   ├── infraestrutura.html
│   ├── infra_form.html
│   ├── infra_detalhes.html
│   ├── funcoes.html
│   └── funcao_form.html
└── static/              # Arquivos estáticos (CSS, JS, imagens)
```

## 🚀 Como Executar

### 1. Preparar Ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt                                    
```                                   

### 3. Executar Aplicação

```bash
python app.py
```

### 4. Acessar Sistema

Abra seu navegador e acesse: `http://127.0.0.1:5000`

**Login padrão:**
- Usuário: `Exponencial`
- Senha: `1234`

## 👤 Níveis de Acesso

### 🔑 Admin
- Acesso total ao sistema
- Gerenciar usuários
- Deletar chamados e equipamentos
- Todas as funcionalidades de técnico

### 🔧 Técnico
- Gerenciar chamados (atribuir, resolver)
- Cadastrar e editar equipamentos
- Acessar chat de suporte
- Visualizar todas as estatísticas

### 👤 Usuário - Acesso Básico

#### ✅ Permitido
- ✓ Criar novos chamados
- ✓ Visualizar próprios chamados
- ✓ Editar próprios chamados
- ✓ Visualizar dashboard básico
- ✓ Comentar em chamados próprios

#### ❌ Negado
- ✗ Visualizar chamados de outros usuários
- ✗ Deletar chamados
- ✗ Atribuir chamados para técnicos
- ✗ Gerenciar equipamentos
- ✗ Gerenciar usuários
- ✗ Acessar funções administrativas

> 💡 **Gerenciar Permissões**: Para alterar permissões de um usuário, acesse:
> 1. Menu lateral → **Usuários**
> 2. Clique no botão **Editar** do usuário desejado
> 3. Altere o **Tipo de Usuário** (Usuário/Técnico/Admin)
> 4. Salve as alterações

## 🎨 Design e Interface

- **Cores**: Azul escuro (#1e3a8a) e cinza claro
- **Layout**: Painel administrativo com menu lateral
- **Responsivo**: Funciona em desktop e mobile
- **Componentes**: Cards, modais, tabelas, gráficos
- **Ícones**: Bootstrap Icons para melhor UX

## 🔧 Configurações

### Banco de Dados
- SQLite para desenvolvimento
- Criação automática de tabelas
- Usuário admin criado automaticamente

### Segurança
- Senhas hasheadas com Werkzeug
- Sessões seguras com Flask-Login
- Validação de permissões em todas as rotas

## 📈 Funcionalidades Implementadas Recentemente

- [x] **Sistema de Funções/Cargos** - Gerenciamento de cargos e níveis de acesso

## 📈 Funcionalidades Futuras

- [ ] Integração com OpenAI API para chat inteligente
- [ ] Notificações por email
- [ ] Relatórios em PDF
- [ ] API REST completa
- [ ] Integração com Active Directory
- [ ] Sistema de SLA
- [ ] Anexos em chamados 

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas, entre em contato através dos canais oficiais da empresa.

---

**Desenvolvido com ❤️ para otimizar o suporte técnico da empresa**
