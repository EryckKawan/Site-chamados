# 🏢 Guia de Implementação em Rede Corporativa

## 🎯 Objetivo
Disponibilizar o Sistema de Chamados TI para toda a empresa acessar via rede interna.

---

## 🚀 Opção 1: Servidor Windows na Rede Local (RECOMENDADO PARA COMEÇAR)

### ⏱️ Tempo: ~30 minutos

### 📋 Requisitos:
- Windows Server ou Windows 10/11
- Acesso de admin ao servidor
- Rede local funcional
- Python instalado

### Passos:

#### 1️⃣ **Preparar o Servidor**

```powershell
# Copiar pasta TI para o servidor
# Exemplo: C:\inetpub\chamados_ti

# Navegar até a pasta
cd C:\inetpub\chamados_ti

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
pip install waitress  # Servidor WSGI para Windows
```

#### 2️⃣ **Atualizar app.py para Rede**

Modifique a última linha do `app.py`:

```python
if __name__ == '__main__':
    init_db()
    print("🚀 Sistema de Chamados TI iniciado!")
    print("📱 Acesse via rede: http://[IP-DO-SERVIDOR]:5000")
    print("🔑 Login: Exponencial / 1234")
    # TROCAR AQUI: 127.0.0.1 → 0.0.0.0 (aceitar conexões externas)
    app.run(debug=False, host='0.0.0.0', port=5000)
```

#### 3️⃣ **Liberar Porta no Firewall**

```powershell
# Abrir PowerShell como Administrador
New-NetFirewallRule -DisplayName "Chamados TI" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

#### 4️⃣ **Iniciar o Servidor**

**Opção A - Manual (para teste):**
```powershell
python app.py
```

**Opção B - Como Serviço Windows (RECOMENDADO):**

Crie arquivo `start_service.bat`:
```batch
@echo off
cd C:\inetpub\chamados_ti
call venv\Scripts\activate
python -m waitress --host=0.0.0.0 --port=5000 app:app
```

Use **NSSM** para criar serviço Windows:
```powershell
# Download NSSM: https://nssm.cc/download
nssm install ChamadosTI "C:\inetpub\chamados_ti\start_service.bat"
nssm start ChamadosTI
```

#### 5️⃣ **Descobrir IP do Servidor**

```powershell
ipconfig
# Procure por "Endereço IPv4" da sua rede local
# Exemplo: 192.168.1.100
```

#### 6️⃣ **Acessar de Outros Computadores**

Nos computadores da empresa, acessar:
```
http://192.168.1.100:5000
```
*(Substitua pelo IP do seu servidor)*

---

## 🌐 Opção 2: IIS (Internet Information Services) - Windows Server

### Para ambientes corporativos grandes

#### Requisitos:
- Windows Server
- IIS instalado
- Python instalado

#### Passos:

1. **Instalar Python no IIS:**
   - Baixar HttpPlatformHandler do IIS
   - Instalar no servidor

2. **Criar site no IIS:**
   - Abrir IIS Manager
   - Add Website
   - Nome: ChamadosTI
   - Caminho: C:\inetpub\chamados_ti
   - Porta: 80

3. **Configurar web.config:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpPlatformHandler" path="*" verb="*" 
           modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="C:\inetpub\chamados_ti\venv\Scripts\python.exe"
                  arguments="C:\inetpub\chamados_ti\app.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="C:\inetpub\chamados_ti\logs\log.txt">
      <environmentVariables>
        <environmentVariable name="FLASK_ENV" value="production" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
```

4. **Acessar:**
   - Internamente: `http://nome-servidor/`
   - Externamente (se configurado): `http://seu-dominio.com.br/`

---

## 🐧 Opção 3: Servidor Linux (Ubuntu) na Rede

### Para ambientes que preferem Linux

```bash
# 1. Instalar dependências
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx -y

# 2. Copiar projeto
sudo cp -r TI /var/www/chamados_ti
cd /var/www/chamados_ti

# 3. Ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 4. Criar serviço systemd
sudo nano /etc/systemd/system/chamados_ti.service
```

**Conteúdo do serviço:**
```ini
[Unit]
Description=Sistema de Chamados TI
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/chamados_ti
Environment="PATH=/var/www/chamados_ti/venv/bin"
ExecStart=/var/www/chamados_ti/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# 5. Iniciar serviço
sudo systemctl start chamados_ti
sudo systemctl enable chamados_ti

# 6. Configurar Nginx (opcional)
sudo nano /etc/nginx/sites-available/chamados_ti
```

---

## 📡 Acesso via Domínio Interno

### Configurar DNS Interno da Empresa

**Opção A - Editar hosts em cada PC (temporário):**

Windows: `C:\Windows\System32\drivers\etc\hosts`
```
192.168.1.100  chamados.empresa.local
```

**Opção B - Servidor DNS da empresa (permanente):**
1. Acessar servidor DNS (geralmente Active Directory)
2. Criar registro A:
   - Nome: `chamados`
   - IP: `192.168.1.100`
3. Agora todos acessam: `http://chamados.empresa.local:5000`

---

## 🔒 Segurança Corporativa

### Checklist de Segurança:

- [ ] **SECRET_KEY forte** no app.py
- [ ] **DEBUG = False** em produção
- [ ] **Firewall** liberando apenas porta 5000
- [ ] **Backup automático** diário do banco
- [ ] **HTTPS** (certificado interno ou Let's Encrypt)
- [ ] **Senhas fortes** para todos os usuários
- [ ] **Logs** de acesso habilitados
- [ ] **Antivírus** permitindo Python
- [ ] **Atualizar** senha padrão do admin

### Implementar HTTPS Interno:

```bash
# Gerar certificado self-signed
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Atualizar app.py
app.run(debug=False, host='0.0.0.0', port=5000, 
        ssl_context=('cert.pem', 'key.pem'))
```

---

## 📊 Monitoramento

### Ferramentas Recomendadas:

1. **Logs de Acesso:**
   ```python
   # Adicionar no app.py
   import logging
   logging.basicConfig(filename='access.log', level=logging.INFO)
   ```

2. **Uptime Monitoring:**
   - Script PowerShell verificando a cada 5 min
   - Email se servidor cair

3. **Backup Automático:**

**Windows Task Scheduler:**
```batch
@echo off
cd C:\inetpub\chamados_ti
copy chamados_ti.db "backups\backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db"
```

---

## 👥 Gerenciamento de Usuários da Empresa

### Estratégia Recomendada:

1. **Criar usuário para cada funcionário:**
   - Login: usar nome de usuário da rede
   - Cargo: conforme função
   - Senha inicial: trocar no primeiro login

2. **Estrutura de Cargos:**
   ```
   admin (TI)
   ├─ tech (Técnicos de TI)
   └─ user (Funcionários)
   ```

3. **Integração com Active Directory (futuro):**
   - Implementar LDAP/AD authentication
   - Sincronização automática de usuários

---

## 🎯 Configuração Rápida para Empresa

### Script Completo para Windows Server:

```powershell
# 1. Variáveis
$AppPath = "C:\inetpub\chamados_ti"
$IP_Servidor = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Ethernet).IPAddress

# 2. Configurar
cd $AppPath
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 3. Iniciar servidor
Write-Host "🚀 Iniciando servidor..."
Write-Host "📱 URL: http://${IP_Servidor}:5000"
Write-Host "🔑 Login: Exponencial / 1234"
python app.py
```

### Salve como: `iniciar_servidor.ps1`

---

## 📱 Como os Funcionários Acessam

### Distribuir para a Equipe:

**Email/Comunicado:**
```
📢 NOVO SISTEMA DE CHAMADOS TI

Acesse: http://chamados.empresa.local:5000
ou
http://192.168.1.100:5000

Login: Seu nome de usuário
Senha: (fornecida pelo TI)

Dúvidas? Entre em contato com o TI.
```

### Criar Atalho na Área de Trabalho:

**Arquivo `Chamados TI.url`:**
```ini
[InternetShortcut]
URL=http://192.168.1.100:5000
IconIndex=0
```

Distribuir via GPO (Group Policy) ou manualmente.

---

## 💾 Backup e Recuperação

### Backup Automático Diário:

**Script PowerShell:** `backup_diario.ps1`
```powershell
$BackupPath = "C:\Backups\ChamadosTI"
$DataAtual = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupPath\backup_$DataAtual.db"

# Criar pasta se não existir
New-Item -ItemType Directory -Force -Path $BackupPath

# Copiar banco
Copy-Item "C:\inetpub\chamados_ti\chamados_ti.db" $BackupFile

# Manter apenas últimos 30 dias
Get-ChildItem $BackupPath -Filter *.db | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
    Remove-Item

Write-Host "✅ Backup criado: $BackupFile"
```

**Agendar no Task Scheduler:**
- Diariamente às 23h
- Executar como SYSTEM
- Comando: `powershell.exe -File C:\scripts\backup_diario.ps1`

---

## 🔧 Manutenção

### Comandos Úteis:

```powershell
# Ver logs
Get-Content C:\inetpub\chamados_ti\logs\access.log -Tail 50

# Reiniciar serviço
Restart-Service ChamadosTI

# Ver processos Python
Get-Process python

# Backup manual
Copy-Item chamados_ti.db "backup_manual_$(Get-Date -Format 'yyyyMMdd').db"
```

---

## 📊 Capacidade e Performance

### Estimativas:

| Usuários Simultâneos | Configuração Mínima |
|---------------------|---------------------|
| 1-10 usuários | PC comum (4GB RAM) |
| 10-50 usuários | Servidor (8GB RAM, SSD) |
| 50-200 usuários | Servidor dedicado (16GB RAM) |
| 200+ usuários | Cluster/Load Balancer |

### Otimizações:

```python
# app.py - Para muitos usuários simultâneos
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000, threads=8)
```

---

## ✅ Checklist de Implementação

### Antes de Liberar para Empresa:

- [ ] Servidor configurado e testado
- [ ] IP fixo configurado no servidor
- [ ] Porta 5000 liberada no firewall
- [ ] Backup automático configurado
- [ ] Senha padrão alterada
- [ ] Usuários criados para equipe TI
- [ ] Testado de vários computadores
- [ ] DNS interno configurado (opcional)
- [ ] Documentação para usuários
- [ ] Treinamento da equipe TI

---

## 🎓 Treinamento da Equipe

### Material para Distribuir:

1. **Manual do Usuário** (criar PDF)
2. **Vídeo tutorial** (5 min)
3. **FAQ** com perguntas comuns
4. **Suporte** - canal para dúvidas

---

## 🚀 DEPLOY RÁPIDO (15 MINUTOS)

### Script Automatizado para Windows:

Salve como `deploy_rede_empresa.ps1`:

```powershell
# Configurações
$AppPath = "C:\ChamadosTI"
$Port = 5000

# Obter IP do servidor
$IP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Ethernet*)[0].IPAddress

Write-Host "🚀 DEPLOY DO SISTEMA DE CHAMADOS TI" -ForegroundColor Green
Write-Host "=" * 50

# 1. Copiar arquivos
Write-Host "`n📁 1. Copiando arquivos..." -ForegroundColor Yellow
Copy-Item -Path ".\*" -Destination $AppPath -Recurse -Force

# 2. Criar ambiente virtual
Write-Host "`n🔧 2. Configurando ambiente..." -ForegroundColor Yellow
cd $AppPath
python -m venv venv
& .\venv\Scripts\activate
pip install -r requirements.txt
pip install waitress

# 3. Configurar firewall
Write-Host "`n🔥 3. Configurando firewall..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Chamados TI - Port $Port" `
    -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow -Force

# 4. Atualizar app.py para rede
Write-Host "`n📝 4. Atualizando configurações..." -ForegroundColor Yellow
(Get-Content app.py) -replace "host='127.0.0.1'", "host='0.0.0.0'" | Set-Content app.py
(Get-Content app.py) -replace "debug=True", "debug=False" | Set-Content app.py

# 5. Iniciar servidor
Write-Host "`n✅ DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "=" * 50
Write-Host "`n📱 Acesse de qualquer PC da rede:" -ForegroundColor Cyan
Write-Host "   http://${IP}:${Port}" -ForegroundColor White
Write-Host "`n🔑 Login padrão:" -ForegroundColor Cyan
Write-Host "   Usuário: Exponencial" -ForegroundColor White
Write-Host "   Senha: 1234" -ForegroundColor White
Write-Host "`n⚠️  Altere a senha após primeiro acesso!" -ForegroundColor Yellow
Write-Host "`n🚀 Iniciando servidor..." -ForegroundColor Green

# Usar waitress (melhor para Windows)
python -m waitress --host=0.0.0.0 --port=$Port app:app
```

### Execute como Administrador:
```powershell
powershell -ExecutionPolicy Bypass -File deploy_rede_empresa.ps1
```

---

## 📱 Acesso via Dispositivos Móveis

Funcionários podem acessar de celulares/tablets conectados à mesma rede WiFi da empresa!

---

## 🎯 RESUMO - 3 Passos Rápidos

1. **No Servidor:**
   ```powershell
   cd C:\Users\Eryck\Documents\TI
   python app.py
   # TROCAR host='127.0.0.1' para host='0.0.0.0'
   ```

2. **Liberar Firewall:**
   ```powershell
   New-NetFirewallRule -DisplayName "Chamados TI" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
   ```

3. **Descobrir IP e Compartilhar:**
   ```powershell
   ipconfig
   # Compartilhar IP com a equipe
   # Exemplo: http://192.168.1.100:5000
   ```

---

## 💡 Recomendação Final

**Para começar HOJE:**
1. Modificar `host='0.0.0.0'` no app.py
2. Liberar porta no firewall
3. Compartilhar IP com equipe

**Para produção séria (próxima semana):**
1. Servidor dedicado Windows/Linux
2. Configurar como serviço
3. Backup automático
4. DNS interno configurado

**Quer que eu modifique o app.py agora para aceitar conexões da rede?** 🚀

