#!/bin/bash
# Script para iniciar o Spotify Mega Mixer (Versão Web)

# Caminho do diretório atual
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================="
echo "🎵 Inicializando Spotify Mega Mixer (Web App)..."
echo "=================================================="

# Verificar se o venv existe
if [ ! -d "venv" ]; then
    echo "⚠️  Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Instalando dependências..."
    pip install spotipy python-dotenv streamlit
else
    source venv/bin/activate
fi

# Garantir que streamlit está instalado
if ! pip show streamlit > /dev/null; then
    echo "📦 Instalando Streamlit..."
    pip install streamlit
fi

echo "🚀 Abrindo no navegador..."
sleep 2

# Iniciar o aplicativo
if command -v xdg-open &> /dev/null; then
    # Linux
    streamlit run app.py
elif command -v open &> /dev/null; then
    # Mac
    streamlit run app.py
else
    # Outros
    streamlit run app.py
fi
