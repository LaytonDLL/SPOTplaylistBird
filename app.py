
import streamlit as st
import os
import time
import random
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Configurações de Página (Deve ser a primeira chamada Streamlit)
st.set_page_config(
    page_title="Spotify Mega Mixer",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Carregar variáveis de ambiente
load_dotenv()

# ==========================================
# CONFIGURAÇÕES E CONSTANTES
# ==========================================
MAX_TRACKS = 100000
PLAYLIST_LIMIT = 10000
TRACKS_PER_REQUEST = 50
SEARCH_LIMIT = 20
SAFE_MODE_DELAY_MIN = 3
SAFE_MODE_DELAY_MAX = 5

AVAILABLE_GENRES = [
    "acoustic", "afrobeat", "alt-rock", "alternative", "alternative-metal", "ambient", "anime",
    "black-metal", "bluegrass", "blues", "bossanova", "brazil", "breakbeat",
    "british", "cantopop", "chicago-house", "children", "chill", "classical",
    "club", "comedy", "country", "dance", "dancehall", "death-metal", "deep-house",
    "detroit-techno", "disco", "disney", "drum-and-bass", "dub", "dubstep", "edm",
    "electro", "electronic", "emo", "emotional", "folk", "forro", "french", "funk", "garage",
    "german", "gospel", "goth", "grindcore", "groove", "grunge", "guitar",
    "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal", "hip-hop",
    "holidays", "honky-tonk", "house", "idm", "indian", "indie", "indie-pop",
    "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz",
    "k-pop", "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc",
    "metalcore", "minimal-techno", "movies", "mpb", "new-age", "new-release",
    "opera", "pagode", "party", "philippines-opm", "piano", "pop", "pop-film",
    "post-dubstep", "power-pop", "progressive-house", "progressive-metalcore", "psych-rock", "punk",
    "punk-rock", "r-n-b", "rainy-day", "reggae", "reggaeton", "road-trip",
    "rock", "rock-n-roll", "rockabilly", "romance", "sad", "salsa", "samba",
    "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep", "songwriter",
    "soul", "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop",
    "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"
]

# ==========================================
# ESTILOS CUSTOMIZADOS (CSS)
# ==========================================
st.markdown("""
<style>
    /* 1. BACKGROUND: Sunny Landscape */
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?q=80&w=2074&auto=format&fit=crop'); 
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .stApp::before { display: none; }

    /* 2. THE AURORA GLASS CARD (99% Match) */
    div[data-testid="column"]:nth-of-type(2) > div {
        /* Gradiente Violeta -> Verde Ciano (cópia exata da ref) */
        background: linear-gradient(125deg, rgba(80, 40, 255, 0.85) 0%, rgba(0, 200, 255, 0.6) 50%, rgba(50, 255, 150, 0.7) 100%) !important;
        
        /* Efeitos de Vidro Espesso */
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 40px !important;
        padding: 50px 30px !important;
        margin-top: 60px;
        
        /* Borda de luz refletida (top/left bright, bottom/right dark) */
        border-top: 2px solid rgba(255,255,255,0.6);
        border-left: 2px solid rgba(255,255,255,0.4);
        border-right: 1px solid rgba(255,255,255,0.1);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        
        /* Sombras e Brilhos */
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.5), /* Sombra projetada */
            inset 0 0 0 1px rgba(255, 255, 255, 0.1), /* Linha fina interna */
            inset 0 20px 40px rgba(255, 255, 255, 0.2); /* Reflexo superior */
    }

    /* 3. INPUTS (Cápsulas indentadas) */
    .stTextInput > div > div > input {
        /* Fundo branco semi-transparente leitoso */
        background: rgba(255, 255, 255, 0.25) !important;
        border: none !important;
        border-top: 1px solid rgba(255,255,255,0.4) !important;
        color: white !important;
        
        /* Forma de Cápsula Perfeita */
        border-radius: 999px !important; 
        height: 60px;
        text-align: center; /* Texto centralizado como na imagem */
        font-size: 18px;
        font-weight: 500;
        
        /* Sombra interna para dar profundidade (indentado) */
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        backdrop-filter: blur(5px);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus {
        background: rgba(255, 255, 255, 0.35) !important;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.1), 0 0 15px rgba(255, 255, 255, 0.3) !important;
    }

    /* 4. BUTTON (Botão Roxo Brilhante) */
    .stButton > button {
        /* Gradiente Roxo Profundo -> Azul Neon (estilo o botão 'Create Playlist') */
        background: linear-gradient(180deg, #6a30fb 0%, #4620cf 100%) !important;
        
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-top: 1px solid rgba(255,255,255,0.6) !important;
        color: white !important;
        
        border-radius: 999px !important; /* Pílula */
        padding: 12px 40px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        
        /* Sombra brilhante roxa */
        box-shadow: 0 5px 15px rgba(80, 20, 200, 0.5), inset 0 2px 3px rgba(255,255,255,0.3) !important;
        
        /* Centralizar */
        display: block;
        margin: 20px auto 0 auto !important;
        width: auto !important;
        min-width: 200px;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(80, 20, 200, 0.7) !important;
        background: linear-gradient(180deg, #7a40ff 0%, #5630df 100%) !important;
    }

    /* TYPOGRAPHY */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    h1, h2, h3, p, label {
        font-family: 'Poppins', sans-serif !important;
        color: #FFFFFF !important;
        text-align: center; /* Tudo centralizado */
    }
    
    h1 {
        font-weight: 600;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Esconder labels dos inputs para ficar igual a imagem (nome dentro do placeholder) */
    label { display: none; }
    
    /* Expander estilo vidro escuro */
    div[data-testid="stExpander"] {
        background: rgba(0,0,0,0.3) !important;
        border: none;
        border-radius: 15px;
        color: white;
    }
    
    /* Clean UI */
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# LÓGICA PRINCIPAL (CLASSES E FUNÇÕES)
# ==========================================

class SpotifyMegaMixerApp:
    def __init__(self):
        self.sp = None
        self.user_id = None
        
        # State Management
        if 'page' not in st.session_state:
            st.session_state.page = 'auth'
        if 'auth_token' not in st.session_state:
            st.session_state.auth_token = ''
        if 'logs' not in st.session_state:
            st.session_state.logs = []

    def log(self, message):
        """Adiciona log ao estado para renderizar na UI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{timestamp}] {message}")
        # Manter apenas os últimos 50 logs
        if len(st.session_state.logs) > 50:
            st.session_state.logs.pop(0)

    def smart_sleep(self):
        delay = random.uniform(SAFE_MODE_DELAY_MIN, SAFE_MODE_DELAY_MAX)
        time.sleep(delay)

    def authenticate_with_token(self, token):
        """Tenta autenticar com o token fornecido"""
        try:
            # Limpeza do token (remover Bearer, aspas, etc)
            clean_token = token
            if "Bearer" in clean_token:
                clean_token = clean_token.split("Bearer")[-1]
            clean_token = clean_token.replace("'", "").replace('"', "").replace("\\", "").strip()
            
            # Configurar com timeout curto e SEM retries para evitar travamento em caso de bloqueio (429)
            self.sp = spotipy.Spotify(
                auth=clean_token,
                requests_timeout=10,
                status_retries=0
            )
            
            # Testar conexão
            with st.spinner("Validando token..."):
                user_info = self.sp.current_user()
            
            self.user_id = user_info['id']
            
            st.session_state.user_info = user_info
            st.session_state.sp_instance = self.sp
            st.session_state.page = 'mixer'
            # st.success(f"Autenticado como: **{user_info['display_name']}**") # Removido para transição mais rápida
            return True
            
        except spotipy.exceptions.SpotifyException as e:
            st.error(f"❌ Erro {e.http_status}: {e.msg}")
            
            # Análise Profunda do Erro
            with st.expander("🕵️‍♂️ Detalhes Técnicos (Análise Profunda)", expanded=True):
                st.markdown("### Cabeçalhos da Resposta (Headers)")
                st.json(e.headers)
                
                if e.http_status == 429:
                    retry_after_seconds = int(e.headers.get("Retry-After", 0))
                    
                    if retry_after_seconds > 0:
                        from datetime import timedelta
                        
                        # Cálculos de tempo
                        wait_duration = timedelta(seconds=retry_after_seconds)
                        release_time = datetime.now() + wait_duration
                        
                        hours = retry_after_seconds // 3600
                        minutes = (retry_after_seconds % 3600) // 60
                        seconds = retry_after_seconds % 60
                        
                        readable_time = ""
                        if hours > 0: readable_time += f"{hours}h "
                        if minutes > 0: readable_time += f"{minutes}m "
                        readable_time += f"{seconds}s"
                        
                        st.error(f"⛔ **BLOQUEIO ATIVO**: Você precisa esperar **{readable_time}**.")
                        st.info(f"🕒 Horário estimado de liberação: **{release_time.strftime('%H:%M:%S')}**")
                    else:
                        st.error("⛔ **RATE LIMIT**: Bloqueado, mas o tempo de espera não foi informado.")

                    st.markdown("""
                    **O que isso significa?**
                    O erro `429 Too Many Requests` é uma **punição temporária** do Spotify.
                    Não adianta tentar de novo agora. O bloqueio é no servidor deles.
                    """)
                elif e.http_status == 401:
                    st.warning("⚠️ O Token parece inválido ou expirado.")
            
            return False
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
            return False

    def search_tracks(self, genres, target_count, progress_bar, status_text):
        """Busca músicas pelos gêneros"""
        sp = st.session_state.sp_instance
        track_uris = set()
        tracks_per_genre = int(target_count / len(genres)) + 1
        
        self.log(f"Iniciando busca para: {', '.join(genres)}")
        
        for idx, genre in enumerate(genres):
            status_text.text(f"🔍 Processando gênero: {genre} ({idx+1}/{len(genres)})")
            
            genre_tracks = set()
            
            # --- Estratégia 1: Recomendações ---
            if genre in AVAILABLE_GENRES:
                try:
                    results = sp.recommendations(seed_genres=[genre], limit=TRACKS_PER_REQUEST, min_popularity=0)
                    for track in results.get('tracks', []):
                        if track.get('uri'): genre_tracks.add(track['uri'])
                    self.smart_sleep()
                except Exception: pass
            
            # --- Estratégia 2: Busca por termos ---
            search_terms = [f"genre:\"{genre}\"", f"tag:{genre}", f"{genre} playlist", f"{genre} mix", genre]
            
            for term in search_terms:
                if len(genre_tracks) >= tracks_per_genre: break
                
                offset = 0
                while offset < 100 and len(genre_tracks) < tracks_per_genre:
                    try:
                        results = sp.search(q=term, type='track', limit=SEARCH_LIMIT, offset=offset)
                        items = results.get('tracks', {}).get('items', [])
                        if not items: break
                        
                        for track in items:
                            if track.get('uri'): genre_tracks.add(track['uri'])
                        
                        offset += SEARCH_LIMIT
                        self.smart_sleep()
                    except Exception: break
            
            self.log(f"Encontradas {len(genre_tracks)} músicas para '{genre}'")
            track_uris.update(genre_tracks)
            
            # Atualizar barra de progresso (0-50% reservada para busca de faixas diretas)
            current_progress = int((idx + 1) / len(genres) * 50)
            progress_bar.progress(current_progress)

        # --- Estratégia 3: Buscar em Playlists (Complementar) ---
        if len(track_uris) < target_count:
            status_text.text("📋 Buscando em Playlists de terceiros para complementar...")
            for idx, genre in enumerate(genres):
                if len(track_uris) >= target_count: break
                
                try:
                    playlist_results = sp.search(q=genre, type='playlist', limit=5)
                    self.smart_sleep()
                    
                    for playlist in playlist_results.get('playlists', {}).get('items', []):
                        if len(track_uris) >= target_count: break
                        if playlist and playlist.get('id'):
                            try:
                                playlist_tracks = sp.playlist_tracks(playlist['id'], limit=30)
                                for item in playlist_tracks.get('items', []):
                                    track = item.get('track')
                                    if track and track.get('uri') and not track['uri'].startswith('spotify:local:'):
                                        track_uris.add(track['uri'])
                                self.smart_sleep()
                            except Exception: continue
                except Exception: pass
                
                # Atualizar barra (50-70%)
                current_progress = 50 + int((idx + 1) / len(genres) * 20)
                progress_bar.progress(current_progress)

        track_list = list(track_uris)
        random.shuffle(track_list)
        return track_list[:target_count]

    def create_and_fill_playlists(self, genres, all_tracks, progress_bar, status_text):
        sp = st.session_state.sp_instance
        user_id = st.session_state.user_info['id']
        
        total_found = len(all_tracks)
        total_vols = (total_found // PLAYLIST_LIMIT) + (1 if total_found % PLAYLIST_LIMIT > 0 else 0)
        
        links = []
        
        for i in range(0, total_found, PLAYLIST_LIMIT):
            vol_tracks = all_tracks[i : i + PLAYLIST_LIMIT]
            vol_num = (i // PLAYLIST_LIMIT) + 1
            
            # Detalhes da Playlist
            timestamp = datetime.now().strftime("%Y-%m-%d")
            title_genres = ", ".join(genres[:2]).title()
            if len(genres) > 2: title_genres += " & More"
            
            name = f"🎵 {title_genres} Mix"
            if total_vols > 1: name += f" - Vol. {vol_num}/{total_vols}"
            
            desc = f"Super Mix gerado com: {', '.join(genres)}. {len(vol_tracks)} músicas. Criado em {timestamp}."
            if total_vols > 1: desc += f" (Parte {vol_num}/{total_vols})"
            
            status_text.text(f"💾 Criando Playlist Volume {vol_num}...")
            
            try:
                # Criar
                playlist = sp.user_playlist_create(
                    user=user_id,
                    name=name,
                    public=True,
                    description=desc
                )
                playlist_id = playlist['id']
                playlist_url = playlist['external_urls']['spotify']
                links.append((name, playlist_url))
                
                self.log(f"Playlist criada: {name}")
                
                # Adicionar Músicas
                added_count = 0
                for j in range(0, len(vol_tracks), TRACKS_PER_REQUEST):
                    batch = vol_tracks[j:j + TRACKS_PER_REQUEST]
                    try:
                        sp.playlist_add_items(playlist_id, batch)
                        added_count += len(batch)
                        self.smart_sleep()
                        
                        # Progresso do Volume (70-100%)
                        overall_completion = 70 + int((vol_num / total_vols) * 30 * ((j + len(batch)) / len(vol_tracks)))
                        if overall_completion > 100: overall_completion = 100
                        progress_bar.progress(overall_completion)
                        
                        status_text.text(f"📥 Adicionando músicas ao Vol. {vol_num}: {added_count}/{len(vol_tracks)}")
                        
                    except Exception as e:
                        self.log(f"Erro ao adicionar lote: {e}")
                
            except Exception as e:
                self.log(f"Erro crítico ao criar playlist: {e}")
                st.error(f"Erro ao criar playlist: {e}")
        
        return links

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================

def main():
    app = SpotifyMegaMixerApp()

    # --- PÁGINA 1: AUTENTICAÇÃO ---
    if st.session_state.page == 'auth':
        # Header Moderno (Hero)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 3rem; margin-bottom: 10px; text-shadow: 0 0 20px rgba(29, 185, 84, 0.6);">
                <span style="color: #1DB954;">SPOTIFY</span> <span style="color: #FFFFFF;">MEGA MIXER</span>
            </h1>
            <p style="font-family: 'Poppins', sans-serif; font-size: 1.2rem; color: #b3b3b3; max-width: 600px; margin: 0 auto;">
                A ferramenta definitiva para criar playlists infinitas baseadas em seus gêneros favoritos.
                Seguro, rápido e automatizado.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Layout Centralizado
        col1, col2, col3 = st.columns([1, 6, 1])
        
        with col2:
            st.markdown("### 🔑 Acesso Necessário")
            
            with st.expander("📝 Passo a passo para obter seu Token (Clique aqui)", expanded=False):
                st.markdown("""
                1. 🔗 Acesse o **[Spotify Developer Console](https://developer.spotify.com/console/post-playlists/)**.
                2. 🟢 Clique no botão verde **GET TOKEN**.
                3. ✅ Marque: `playlist-modify-public` e `playlist-modify-private`.
                4. 🖱️ Clique em **Request Token**.
                5. 📋 Copie o código longo do campo **OAuth Token**.
                """)
            
            token_input = st.text_input("Cole seu Token do Spotify:", type="password", placeholder="Bearer BQCL-...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 INICIAR CONEXÃO"):
                if token_input:
                    if app.authenticate_with_token(token_input):
                        st.rerun()
                else:
                    st.warning("⚠️ Por favor, cole o token para continuar.")

    # --- PÁGINA 2: O MIXER (CONFIGURAÇÃO) ---
    elif st.session_state.page == 'mixer':
        # Sidebar com INFO do Usuário
        user = st.session_state.user_info
        with st.sidebar:
            if user.get('images'):
                st.image(user['images'][0]['url'], width=100)
            st.markdown(f"### Olá, {user['display_name']}!")
            if st.button("Sair / Trocar Token"):
                st.session_state.page = 'auth'
                st.session_state.auth_token = ''
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📜 Logs Recentes")
            log_container = st.container()
                
        st.title("🎛️ Configurar Mix")
        
        # Seleção de Gêneros (Visual - Conteineres)
        st.subheader("1. Escolha os Estilos")
        st.info("Clique nos estilos abaixo para selecionar (recomendado: 1 a 5 estilos).")
        
        available_genres_sorted = sorted(AVAILABLE_GENRES)
        
        selected_genres = st.pills(
            "Gêneros Disponíveis",
            options=available_genres_sorted,
            default=['pop', 'dance'],
            selection_mode="multi"
        )
        
        # Fallback caso st.pills retorne None (sem seleção inicial)
        if selected_genres is None:
            selected_genres = []
            
        # Tags customizadas
        st.markdown("") # Espaçamento
        custom_tags = st.text_input("➕ Adicionar outro estilo ou tag específica:", placeholder="Ex: gym phonk, dark synthwave")
        if custom_tags:
            extras = [t.strip() for t in custom_tags.split(',') if t.strip()]
            selected_genres.extend(extras)
            st.caption(f"Incluindo extras: {', '.join(extras)}")
        
        # Quantidade de músicas
        track_count = st.slider("Quantidade total de músicas:", 100, MAX_TRACKS, 1000, step=100)
        
        # Botão de Ação
        st.markdown("---")
        if st.button("💿 CRIAR PLAYLISTS"):
            if not selected_genres:
                st.error("Selecione pelo menos um gênero!")
            else:
                # --- PROCESSO DE CRIAÇÃO ---
                status_box = st.empty()
                progress_bar = st.progress(0)
                
                with st.spinner("Iniciando os motores..."):
                    # 1. Buscar
                    all_tracks = app.search_tracks(selected_genres, track_count, progress_bar, status_box)
                    
                    if not all_tracks:
                        st.error("Nenhuma música encontrada com esses critérios. Tente termos mais populares.")
                    else:
                        # 2. Criar
                        links = app.create_and_fill_playlists(selected_genres, all_tracks, progress_bar, status_box)
                        
                        # 3. Sucesso
                        progress_bar.progress(100)
                        status_box.empty()
                        
                        st.balloons()
                        st.success("✅ Processo concluído com sucesso!")
                        
                        st.markdown("### 🔗 Suas Novas Playlists:")
                        for title, url in links:
                            st.markdown(f"""
                            <div class="success-box">
                                <b>{title}</b><br>
                                <a href="{url}" target="_blank" style="color: white; text-decoration: underline;">Abrir no Spotify</a>
                            </div>
                            """, unsafe_allow_html=True)
        
        # Renderizar Logs na Sidebar
        with log_container:
            for log in reversed(st.session_state.logs):
                st.text(log)

if __name__ == "__main__":
    main()
