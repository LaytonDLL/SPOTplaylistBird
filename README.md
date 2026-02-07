# 🎵 SPOTplaylistBird

**Crie Playlists Gigantes no Spotify em Segundos.**

Este projeto permite criar playlists massivas (até 10.000 músicas) baseadas em gêneros musicais, utilizando a API do Spotify. É ideal para descobrir novas músicas ou preencher bibliotecas de acordo com estilos específicos.

![Project Banner](webapp/public/logo.png)

---

## 🚀 Como Usar (Guia Rápido)

### 1. Pré-requisitos
- Ter o **Python 3.8+** instalado.
- Ter o **Node.js 18+** instalado (para a interface visual).
- Uma conta no **Spotify** (Free ou Premium).

### 2. Instalação
Abra o terminal na pasta do projeto e execute:

```bash
# 1. Instalar dependências do Python
pip install spotipy python-dotenv fastapi uvicorn

# 2. Instalar dependências da Interface (React)
cd webapp
npm install
cd ..
```

### 3. Executando o Projeto

O projeto já inclui scripts de inicialização automática para facilitar o uso.

**Windows:**
1. Execute o arquivo `web-spotplaylistbird.bat` (duplo clique).
2. O script procurará automaticamente onde o projeto está instalado e iniciará tudo.

**Linux / macOS:**
1. No terminal, dê permissão de execução:
   ```bash
   chmod +x web-spotplaylistbird.sh
   ```
2. Inicie o launcher:
   ```bash
   ./web-spotplaylistbird.sh
   ```

Este launcher é "inteligente": se você mover o script para outra pasta (ex: Área de Trabalho) ou criar um atalho, ele ainda conseguirá encontrar o projeto original e iniciá-lo corretamente.

---

### Instalação Manual (Alternativa)

Se preferir rodar manualmente:

#### Linux / macOS
```bash
# Dar permissão de execução
chmod +x run.sh

# Iniciar o projeto
./run.sh
```

#### Windows
```cmd
run_windows.bat
```

O navegador abrirá automaticamente em `http://localhost:5173`.

---

## 🔑 Como Obter o Token de Acesso

O projeto utiliza um **Token de Acesso** temporário do Spotify para garantir segurança e funcionar com qualquer conta.

1. Acesse o **Spotify Developer Console** (Link seguro oficial):
   👉 [https://developer.spotify.com/console/post-playlists/](https://developer.spotify.com/console/post-playlists/)

2. Clique no botão verde **GET TOKEN**.

3. Selecione as seguintes permissões (checkboxes):
   - `playlist-modify-public`
   - `playlist-modify-private`

4. Clique em **Request Token**.

5. Faça login na sua conta Spotify (se solicitado).

6. Copie o código longo gerado no campo **OAuth Token**.

7. Cole este código na tela inicial do **SPOTplaylistBird**.

---

## 🛠️ Solução de Problemas Comuns

### "O botão 'Connect' fica carregando infinitamente"
- **Causa**: O token expirou ou é inválido.
- **Solução**: Gere um novo token seguindo os passos acima e tente novamente.

### "Erro 429 ou Rate Limit"
- **Causa**: Você fez muitas requisições em pouco tempo. O Spotify bloqueia temporariamente por segurança.
- **Solução**: Aguarde alguns minutos e tente novamente.

### "Não abre o navegador"
- Tente acessar manualmente: `http://localhost:5173`

---

## 📦 Estrutura do Projeto

- `run.sh`: Script principal de inicialização.
- `server.py`: Servidor Backend (Python/FastAPI) que se comunica com o Spotify.
- `webapp/`: Interface Visual (React/Vite).
- `spotify_filler.py`: Versão somente linha de comando (CLI) alternativa.

## 📝 Licença

Este projeto é de código aberto e destinado a fins educacionais e pessoais. Use com responsabilidade.
