#!/bin/bash
# Launcher Universal para Linux e macOS
# ----------------------------------------------------------------------
# Este script tenta localizar a pasta do projeto automaticamente se não estiver
# sendo executado de dentro dela. Ideal para criar atalhos ou aliases.

# Detecção de OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

# Definições de Cores
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    NC=''
fi

echo "=================================================="
echo -e "${BLUE}🔍 SPOTplaylistBird - Launcher Universal ($MACHINE)${NC}"
echo "=================================================="

# Função para verificar se o diretório é a raiz do projeto
is_project_dir() {
    local dir="$1"
    if [ -f "$dir/run.sh" ] && [ -f "$dir/server.py" ]; then
        return 0
    fi
    return 1
}

# 1. Verificar se já estamos no diretório
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if is_project_dir "$CURRENT_DIR"; then
    echo -e "${GREEN}✅ Executando de dentro do projeto.${NC}"
    PROJECT_DIR="$CURRENT_DIR"
else
    # 2. Procurar automaticamente
    echo -e "${YELLOW}🔍 Procurando pasta do projeto no sistema...${NC}"
    
    # Locais de busca comuns
    SEARCH_DIRS=(
        "$HOME/Desktop"
        "$HOME/Downloads"
        "$HOME/Documents"
        "$HOME/Projects"
        "$HOME/Projetos"
        "$HOME"
    )

    # Adicionar "Área de Trabalho" se existir (Linux pt-BR)
    if [ -d "$HOME/Área de trabalho" ]; then
        SEARCH_DIRS+=("$HOME/Área de trabalho")
    fi

    FOUND_DIR=""

    # Busca em locais padrão
    for base_dir in "${SEARCH_DIRS[@]}"; do
        if [ -d "$base_dir" ]; then
            for name in "spotify-playlist-filler" "SPOTplaylistBird" "web-spotplaylistbird" "spotify-playlist-filler-main" "spotify-playlist-filler-master"; do
                path="$base_dir/$name"
                
                # Caso 1: A pasta é o projeto
                if [ -d "$path" ]; then
                    if is_project_dir "$path"; then
                        FOUND_DIR="$path"
                        break 2
                    # Caso 2: O projeto está dentro (ex: repo > SPOTplaylistBird)
                    elif [ -d "$path/SPOTplaylistBird" ] && is_project_dir "$path/SPOTplaylistBird"; then
                        FOUND_DIR="$path/SPOTplaylistBird"
                        break 2
                    fi
                fi
            done
        fi
    done

    # Busca Profunda se não encontrar
    if [ -z "$FOUND_DIR" ]; then
        echo "⚠️  Não encontrado nos locais padrão. Realizando busca profunda (max depth 4)..."
        # Find compatível com Linux e macOS (BSD find)
        # Ignora erros de permissão
        RESULTS=$(find "$HOME" -maxdepth 4 -type d \( -name "SPOTplaylistBird" -o -name "spotify-playlist-filler*" \) 2>/dev/null)
        
        for res in $RESULTS; do
            if is_project_dir "$res"; then
                FOUND_DIR="$res"
                break
            elif [ -d "$res/SPOTplaylistBird" ] && is_project_dir "$res/SPOTplaylistBird"; then
                FOUND_DIR="$res/SPOTplaylistBird"
                break
            fi
        done
    fi

    if [ -z "$FOUND_DIR" ]; then
        echo -e "${RED}❌ Erro Crítico: Pasta do projeto não encontrada!${NC}"
        echo "   Certifique-se que o projeto foi baixado para sua Home, Desktop ou Downloads."
        exit 1
    fi

    PROJECT_DIR="$FOUND_DIR"
    echo -e "🚀 Encontrado em: $PROJECT_DIR"
fi

# Navegar e Executar
cd "$PROJECT_DIR"

# Verificar permissões do run.sh
if [ -f "run.sh" ]; then
    chmod +x run.sh
fi

echo -e "${YELLOW}⏳ Iniciando em 5 segundos... (Pressione Enter para pular, Ctrl+C para cancelar)${NC}"
read -t 5 -p ""

echo -e "\n🔥 Iniciando..."
./run.sh
