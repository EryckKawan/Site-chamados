# 📘 Guia de Uso - Gerenciamento de Servidores

## Como Cadastrar Servidores com Diferentes Unidades

### 🎯 Regra Principal
**Importante:** O espaço total e o espaço usado devem sempre estar na **mesma unidade**.

### ✅ Exemplos Corretos

#### Exemplo 1: Servidor com 2 TB total e 500 GB usado

**Opção A - Tudo em TB:**
- Espaço Total: `2` TB
- Espaço Usado: `0.5` TB (500 GB = 0.5 TB)
- Unidade: `TB`

**Opção B - Tudo em GB:**
- Espaço Total: `2048` GB (2 TB = 2048 GB)
- Espaço Usado: `512` GB
- Unidade: `GB`

#### Exemplo 2: Servidor com 500 GB total e 250 GB usado

- Espaço Total: `500` GB
- Espaço Usado: `250` GB
- Unidade: `GB`

#### Exemplo 3: Servidor com 10240 MB total e 5120 MB usado

- Espaço Total: `10240` MB
- Espaço Usado: `5120` MB
- Unidade: `MB`

### ❌ Exemplos Incorretos

**NÃO FAÇA ISSO:**
- Espaço Total: `2` TB
- Espaço Usado: `500` GB ❌ (unidades diferentes!)
- Unidade: `TB`

**Problema:** O sistema vai calcular como se você tivesse 500 TB usado, não 500 GB!

### 🔄 Tabela de Conversão Rápida

| De        | Para      | Fórmula           | Exemplo                |
|-----------|-----------|-------------------|------------------------|
| MB → GB   | ÷ 1024    | 10240 MB ÷ 1024   | = 10 GB               |
| GB → MB   | × 1024    | 500 GB × 1024     | = 512000 MB           |
| GB → TB   | ÷ 1024    | 2048 GB ÷ 1024    | = 2 TB                |
| TB → GB   | × 1024    | 2 TB × 1024       | = 2048 GB             |
| MB → TB   | ÷ 1048576 | 2097152 MB ÷ 1048576 | = 2 TB             |
| TB → MB   | × 1048576 | 2 TB × 1048576    | = 2097152 MB          |

### 💡 Dica Pro

Use a **unidade mais apropriada** para o tamanho do seu servidor:

- **MB**: Para servidores muito pequenos (< 1 GB)
- **GB**: Para servidores médios (1 GB - 1 TB) ⭐ **RECOMENDADO**
- **TB**: Para servidores grandes (> 1 TB)

### 🖥️ Como o Sistema Funciona

1. **Você cadastra** o servidor com todos os valores na mesma unidade
2. **O sistema calcula** automaticamente:
   - Espaço livre = Espaço total - Espaço usado
   - Percentual livre = (Espaço livre / Espaço total) × 100
3. **O sistema exibe** as conversões em MB, GB e TB automaticamente nos botões/dropdowns

### 📊 Exemplo Prático

Você tem um servidor com:
- 2 TB de disco total
- 500 GB já usados
- Quanto livre? 2 TB - 500 GB = ?

**Solução: Converter tudo para a mesma unidade primeiro!**

**Opção 1 - Trabalhar em GB:**
```
2 TB = 2048 GB
500 GB = 500 GB
Livre = 2048 - 500 = 1548 GB
```

**Cadastro no sistema:**
- Espaço Total: `2048`
- Espaço Usado: `500`
- Unidade: `GB`

**Opção 2 - Trabalhar em TB:**
```
2 TB = 2 TB
500 GB = 0.48828125 TB
Livre = 2 - 0.48828125 = 1.51171875 TB
```

**Cadastro no sistema:**
- Espaço Total: `2`
- Espaço Usado: `0.48828125`
- Unidade: `TB`

### 🎨 Visualização no Sistema

Após cadastrar, o sistema mostrará automaticamente:

```
250 GB  [🔄]  ← Clique aqui
    ↓
  ┌─────────────────┐
  │ 256000.00 MB   │
  │ 250.00 GB      │
  │ 0.24 TB        │
  └─────────────────┘
```

### 🛠️ Ferramentas de Conversão

Se precisar converter valores, use a calculadora:

```python
from models.servidor import Servidor

# Converter 500 GB para TB
valor_tb = Servidor.converter_unidade(500, 'GB', 'TB')
print(f"500 GB = {valor_tb} TB")  # Resultado: 0.48828125 TB

# Converter 2 TB para GB
valor_gb = Servidor.converter_unidade(2, 'TB', 'GB')
print(f"2 TB = {valor_gb} GB")  # Resultado: 2048 GB
```

### ⚠️ Avisos Importantes

1. **Sempre use a mesma unidade** para espaço total e usado
2. **Escolha a unidade mais apropriada** (GB é recomendado)
3. **Converta antes de cadastrar** se necessário
4. **O sistema não converte automaticamente** durante o cadastro
5. **Verifique seus cálculos** antes de salvar

### 📞 Precisa de Ajuda?

Se tiver dúvidas sobre qual unidade usar ou como converter, entre em contato com o suporte técnico.

---

**Desenvolvido com ❤️ para facilitar o gerenciamento de servidores**

