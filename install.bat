@echo off
echo ========================================
echo   Sistema de Chamados TI - Instalacao
echo ========================================
echo.

echo [1/4] Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar ambiente virtual
    pause
    exit /b 1
)

echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERRO: Falha ao ativar ambiente virtual
    pause
    exit /b 1
)

echo [3/4] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo [4/4] Inicializando banco de dados...
python run.py --sample
if %errorlevel% neq 0 (
    echo ERRO: Falha ao inicializar banco de dados
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Instalacao concluida com sucesso!
echo ========================================
echo.
echo Para executar o sistema:
echo   1. Ative o ambiente virtual: venv\Scripts\activate
echo   2. Execute: python run.py
echo   3. Acesse: http://127.0.0.1:5000
echo.
echo Login padrao: admin / admin123
echo.
pause
