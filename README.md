# 🎵 Spotify Playlist Filler

Adicione até **10.000 músicas** em uma playlist do Spotify baseado no gênero escolhido!

## 📋 Requisitos

- Python 3.8+
- Conta no Spotify
- Credenciais do Spotify Developer

## 🚀 Instalação

### 1. Instalar dependências

```bash
# Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar credenciais do Spotify

1. Acesse [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Clique em **Create App**
3. Preencha:
   - **App name**: Playlist Filler (ou qualquer nome)
   - **App description**: Script para preencher playlists
   - **Redirect URI**: `http://localhost:8888/callback`
4. Clique em **Settings** e copie:
   - **Client ID**
   - **Client Secret**
5. Configure o arquivo `.env`:

```bash
cp .env.example .env
nano .env  # ou use seu editor preferido
```

Preencha com suas credenciais:
```
SPOTIPY_CLIENT_ID=seu_client_id_aqui
SPOTIPY_CLIENT_SECRET=seu_client_secret_aqui
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

## 🎮 Como usar

```bash
# Ativar ambiente virtual (se não estiver ativo)
source venv/bin/activate

# Executar o script
python spotify_filler.py
```

O script vai:
1. Abrir seu navegador para autenticação
2. Mostrar os gêneros disponíveis
3. Pedir para escolher um gênero
4. Pedir a quantidade de músicas (1-10000)
5. Criar uma nova playlist
6. Adicionar as músicas!

## 🎸 Gêneros disponíveis

O script suporta mais de 100 gêneros, incluindo:

| | | | |
|---|---|---|---|
| rock | pop | hip-hop | electronic |
| jazz | blues | classical | country |
| metal | punk | reggae | r-n-b |
| sertanejo | pagode | mpb | funk |
| k-pop | j-pop | anime | ... |

## ⚠️ Limitações

- **Máximo de 10.000 músicas por playlist** (limite do Spotify)
- O script pode não encontrar 10.000 músicas únicas para todos os gêneros
- Rate limiting da API pode causar lentidão

## 🔧 Solução de Problemas

### Erro de autenticação
- Verifique se as credenciais no `.env` estão corretas
- Certifique-se de que a Redirect URI no Dashboard é exatamente `http://localhost:8888/callback`

### Poucas músicas encontradas
- Alguns gêneros têm menos músicas disponíveis
- Tente gêneros mais populares como `pop`, `rock`, `hip-hop`

### Rate limiting
- O script já inclui delays automáticos
- Se persistir, aguarde alguns minutos e tente novamente

## 📝 Licença

MIT License - Use como quiser!

## 🙏 Créditos

Criado com ❤️ por Antigravity AI usando a biblioteca [Spotipy](https://spotipy.readthedocs.io/)
