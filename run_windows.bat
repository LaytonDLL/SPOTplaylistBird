@echo off
SETLOCAL EnableDelayedExpansion

REM Script de inicialização para Windows
REM Criado para SPOTplaylistBird

echo ==================================================
echo 🚀 Iniciando SPOTplaylistBird (Windows)...
echo ==================================================

REM Matar processos antigos (opcional, requer permissão)
taskkill /F /IM uvicorn.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

REM Verificar e criar venv
IF NOT EXIST "venv" (
    echo ⚠️  Ambiente virtual não encontrado. Criando...
    python -m venv venv
    call venv\Scripts\activate
    echo 📦 Instalando dependências...
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate
)

REM Iniciar Backend em nova janela
echo 🚀 Iniciando Servidor Backend...
start "SPOTplaylistBird Backend" /MIN cmd /k "venv\Scripts\activate && uvicorn server:app --host 0.0.0.0 --port 8000 --reload"

echo Aguardando backend...
timeout /t 3 /nobreak >nul

REM Iniciar Frontend
echo 🎨 Iniciando Interface Frontend...
cd webapp
IF NOT EXIST "node_modules" (
    echo 📦 Instalando dependências do Frontend...
    call npm install
)
start "SPOTplaylistBird Frontend" /MIN cmd /k "npm run dev -- --host"

REM Abrir navegador
echo 🌐 Abrindo plataforma...
timeout /t 4 /nobreak >nul
start http://localhost:5173

echo ==================================================
echo ✅ Sistema iniciado!
echo 📝 Logs estão nas janelas minimizadas.
echo ==================================================
pause
