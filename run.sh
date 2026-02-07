#!/bin/bash

# Matar processos antigos nas portas 8000 e 5173
fuser -k 8000/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null

# Iniciar o Backend (FastAPI) em background
echo "🚀 Iniciando Servidor Backend (FastAPI)..."
source venv/bin/activate
nohup uvicorn server:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend rodando (PID: $BACKEND_PID)"

# Esperar um pouco para o backend subir
sleep 2

# Iniciar o Frontend (React/Vite)
echo "🎨 Iniciando Interface Frontend (React)..."
cd webapp
npm run dev -- --host &
FRONTEND_PID=$!

# Abrir o navegador automaticamente
echo "🌐 Abrindo navegador em http://localhost:5173..."
sleep 3
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173 > /dev/null 2>&1 &
fi

echo "✅ Frontend rodando!"
echo "--------------------------------------------------"
echo "🌐 ACESSE AGORA: http://localhost:5173"
echo "--------------------------------------------------"

# Manter o script rodando e limpar ao sair
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
