# 🔍 Guia de Diagnóstico - Botões de Permissões

## 🎯 Problema
Não consegue clicar nos botões ✅ Permitido / ❌ Negado

## ✅ Correções Aplicadas

### 1. **CSS Melhorado**
- ✅ Adicionado `cursor: pointer`
- ✅ Adicionado `pointer-events: auto`
- ✅ Adicionado `z-index: 10`
- ✅ Adicionado `position: relative`

### 2. **JavaScript com Debug**
- ✅ Console.log em cada etapa
- ✅ Contador de botões encontrados
- ✅ Logs de clique e mudança de estado
- ✅ `e.stopPropagation()` para evitar conflitos

### 3. **Backend Protegido**
- ✅ Try/catch para buscar permissões
- ✅ Lista vazia como fallback
- ✅ Validação de dados

### 4. **Template Protegido**
- ✅ `user_permissions|default([])`
- ✅ ID no container de permissões

## 🧪 Como Testar

### Passo 1: Limpar Cache do Navegador
```
1. Pressione Ctrl + Shift + Delete
2. Limpe "Cache de imagens e arquivos"
3. Feche e abra o navegador
```

### Passo 2: Acessar a Página
```
1. Faça login como Admin
2. Vá para Usuários → Editar usuário
3. Role até a seção "Permissões de Acesso"
```

### Passo 3: Abrir Console do Desenvolvedor
```
Pressione F12 ou Ctrl + Shift + I
```

### Passo 4: Verificar Logs no Console

Você deve ver algo assim:

```
🔧 Carregando sistema de permissões...
✅ DOM carregado
🔘 Botões encontrados: 8
Configurando botão 1: view_chamados
Configurando botão 2: create_chamados
Configurando botão 3: edit_chamados
Configurando botão 4: delete_chamados
Configurando botão 5: assign_chamados
Configurando botão 6: manage_infrastructure
Configurando botão 7: manage_users
Configurando botão 8: access_chat
✅ Sistema de permissões configurado com sucesso!
```

### Passo 5: Clicar em um Botão

Ao clicar, você deve ver:

```
🖱️ Botão clicado: view_chamados
Mudando de true para false
Input hidden atualizado: 0
✅ Atualização concluída
```

## ❌ Possíveis Problemas e Soluções

### Problema 1: Console mostra "0 botões encontrados"
**Causa**: Template não está renderizando os botões
**Solução**:
```bash
# Verifique se o banco de dados tem a tabela
python
>>> from app import get_db_connection
>>> conn = get_db_connection()
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_permissions'")
>>> print(cursor.fetchall())
```

### Problema 2: Console não mostra nada
**Causa**: JavaScript não está carregando
**Solução**:
1. Verifique se o arquivo `base.html` tem `{% block extra_js %}{% endblock %}`
2. Verifique se não há erros de sintaxe JavaScript (F12 → Console)

### Problema 3: Botões aparecem mas não clicam
**Causa**: CSS ou outro elemento sobrepondo
**Solução**:
1. No console do navegador, digite:
```javascript
document.querySelectorAll('.permission-toggle').forEach(btn => {
    btn.style.pointerEvents = 'auto';
    btn.style.zIndex = '9999';
    console.log('Botão ajustado:', btn);
});
```

### Problema 4: Erro ao salvar
**Causa**: Tabela `user_permissions` não existe
**Solução**:
```bash
# Deletar o banco e recriar
rm chamados.db
python app.py
```

## 🔧 Comandos Úteis para Debug

### No Console do Navegador (F12):

```javascript
// Verificar se botões existem
console.log('Botões:', document.querySelectorAll('.permission-toggle'));

// Testar clique programático
document.querySelector('.permission-toggle').click();

// Verificar estilos do botão
let btn = document.querySelector('.permission-toggle');
console.log({
    cursor: window.getComputedStyle(btn).cursor,
    pointerEvents: window.getComputedStyle(btn).pointerEvents,
    zIndex: window.getComputedStyle(btn).zIndex
});

// Forçar click listener
document.querySelector('.permission-toggle').addEventListener('click', function() {
    alert('Clicou!');
});
```

## 📝 Checklist de Verificação

- [ ] Cache do navegador limpo
- [ ] Console aberto (F12)
- [ ] Logs aparecem no console
- [ ] "Botões encontrados: 8" aparece
- [ ] Cursor muda para "pointer" ao passar sobre o botão
- [ ] Botão tem borda verde ou vermelha
- [ ] Ao clicar, aparece log no console
- [ ] Ao clicar, cor do botão muda
- [ ] Ao salvar, dados são persistidos

## 🆘 Ainda Não Funciona?

Se após todos os passos ainda não funcionar:

1. **Tire um print da tela** mostrando a seção de permissões
2. **Copie os logs do console** (F12 → Console → Botão direito → Salvar como...)
3. **Verifique a aba Network** (F12 → Network) ao carregar a página
4. **Verifique erros JavaScript** (F12 → Console, filtro "Errors")

## 🎬 Video Tutorial (se necessário)

Se preferir, grave um vídeo rápido mostrando:
1. Abrindo a página
2. Tentando clicar nos botões
3. Console do desenvolvedor aberto

Isso ajudará a identificar o problema exato!

---

**Última atualização**: Com logs de debug e proteções extras

