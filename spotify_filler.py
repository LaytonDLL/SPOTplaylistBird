#!/usr/bin/env python3
"""
🎵 Spotify Playlist Filler - Adiciona até 10.000 músicas por gênero
Autor: Antigravity AI
"""

import os
import sys
import time
import random
from datetime import datetime
from dotenv import load_dotenv

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    print("❌ Biblioteca spotipy não encontrada.")
    print("Execute: pip install spotipy python-dotenv")
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
MAX_TRACKS = 100000        # Aumentado para 100k (via múltiplos volumes)
PLAYLIST_LIMIT = 10000     # Limite máximo do Spotify por playlist
TRACKS_PER_REQUEST = 50    # Reduzido de 100 para 50 para ser mais seguro
SEARCH_LIMIT = 20          # Reduzido de 50 para 20
SAFE_MODE_DELAY_MIN = 3
SAFE_MODE_DELAY_MAX = 5

# Lista de gêneros disponíveis no Spotify
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

class SpotifyPlaylistFiller:
    def __init__(self):
        self.sp = None
        self.user_id = None

    def smart_sleep(self):
        """Pausa inteligente para evitar bloqueios"""
        delay = random.uniform(SAFE_MODE_DELAY_MIN, SAFE_MODE_DELAY_MAX)
        print(f"   ⏳ Aguardando {delay:.1f}s...", end="\r")
        time.sleep(delay)
        print(" " * 20, end="\r") # Limpa a linha
    
    def authenticate(self):
        """Autentica o usuário no Spotify"""
        print("\n🔐 Autenticando no Spotify...")
        
        # Verificar credenciais
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")
        
        # MODO 1: Tentar autenticação automática (se as credenciais existirem)
        if client_id and client_secret and client_id != "your_client_id_here":
            scope = "playlist-modify-public playlist-modify-private playlist-read-private user-library-read"
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=scope,
                    cache_path=".spotify_cache"
                ))
                user_info = self.sp.current_user()
                self.user_id = user_info['id']
                print(f"✅ Autenticado via App como: {user_info['display_name']} ({self.user_id})")
                return True
            except Exception as e:
                print(f"⚠️ Erro ao autenticar com credenciais: {e}")
                print("Tentando modo manual...")

        # MODO 2: Token Manual (Workaround para o bloqueio do Spotify)
        print("\n⚠️  O MODO AUTOMÁTICO NÃO ESTÁ DISPONÍVEL (Sem credenciais configuradas).")
        print("   Devido ao bloqueio temporário do Spotify para criar novos Apps,")
        print("   vamos usar um TOKEN TEMPORÁRIO gerado no Console do Spotify.")
        
        print("\n📋 SIGA ESTES PASSOS PARA PEGAR O TOKEN:")
        print("   1. Segure CTRL e clique neste link: https://developer.spotify.com/console/post-playlists/")
        print("   2. Clique no botão verde 'GET TOKEN'")
        print("   3. Marque as opções: 'playlist-modify-public' e 'playlist-modify-private'")
        print("   4. Clique em 'Request Token'")
        print("   5. Copie o código longo gerado no campo 'OAuth Token'")
        
        raw_token = input("\n🔑 Cole o Token aqui e aperte ENTER: ").strip()
        
        # Limpeza inteligente do token (caso o usuário cole o comando curl inteiro)
        token = raw_token
        if "Bearer" in token:
            token = token.split("Bearer")[-1]
            
        # Remover aspas, barras e espaços extras
        token = token.replace("'", "").replace('"', "").replace("\\", "").strip()
        
        if len(token) > 10:
            try:
                self.sp = spotipy.Spotify(auth=token)
                user_info = self.sp.current_user()
                self.user_id = user_info['id']
                print(f"✅ Autenticado via Token como: {user_info['display_name']} ({self.user_id})")
                return True
            except Exception as e:
                 print(f"❌ Token inválido ou expirado: {e}")
                 return False
        else:
            print("❌ Token muito curto ou inválido.")
            return False
    
    def show_genres(self):
        """Mostra os gêneros disponíveis"""
        print("\n🎸 Gêneros disponíveis:")
        print("-" * 60)
        
        # Organizar em colunas
        cols = 4
        for i in range(0, len(AVAILABLE_GENRES), cols):
            row = AVAILABLE_GENRES[i:i + cols]
            print("  " + "  |  ".join(f"{g:<15}" for g in row))
        
        print("-" * 60)
    
    def get_genres_input(self):
        """Obtém os gêneros/tags do usuário"""
        print("\n🎸 Digite os gêneros ou estilos musicais (separados por vírgula).")
        print("   Exemplo: japanese hyperpop, hardwave, digicore, experimental pop")
        
        while True:
            raw_input = input("\n🎵 Digite os gêneros (ou 'q' para sair): ").strip().lower()
            
            if raw_input == 'q':
                print("👋 Até logo!")
                sys.exit(0)
            
            if not raw_input:
                continue
            
            # Separar por vírgula e limpar espaços
            genres = [g.strip() for g in raw_input.split(',') if g.strip()]
            
            print(f"✅ Gêneros detectados: {', '.join(genres)}")
            return genres
    
    def get_track_count(self):
        """Obtém a quantidade de músicas desejada"""
        while True:
            try:
                count = input(f"\n🔢 Quantas músicas adicionar? (1-{MAX_TRACKS}, padrão: 10000): ").strip()
                
                if not count:
                    return MAX_TRACKS
                
                count = int(count)
                if 1 <= count <= MAX_TRACKS:
                    return count
                else:
                    print(f"❌ Digite um número entre 1 e {MAX_TRACKS}")
                    
            except ValueError:
                print("❌ Digite um número válido")

    def search_tracks_by_keywords(self, genres_list, target_count):
        """Busca músicas por uma lista de gêneros/tags"""
        track_uris = set()
        tracks_per_genre = int(target_count / len(genres_list)) + 1
        
        print(f"\n🔍 Buscando músicas para: {', '.join(genres_list)}")
        print(f"   (Aproximadamente {tracks_per_genre} músicas por estilo)")
        print(f"   🛡️ MODO SEGURO ATIVADO: Buscas mais lentas para evitar bloqueios.\n")

        for genre in genres_list:
            print(f"\n👉 Processando gênero: '{genre}'...")
            
            genre_tracks = set()
            
            # Estratégia 1: Recomendações (Apenas se for gênero oficial)
            if genre in AVAILABLE_GENRES:
                print("   📡 Obtendo recomendações oficiais...")
                try:
                    results = self.sp.recommendations(seed_genres=[genre], limit=TRACKS_PER_REQUEST, min_popularity=0)
                    for track in results.get('tracks', []):
                        if track.get('uri'): genre_tracks.add(track['uri'])
                    print(f"     → {len(genre_tracks)} encontradas via recomendações")
                    self.smart_sleep()
                except Exception: pass
            
            # Estratégia 2: Busca por nome/tag
            print("   🔎 Buscando por termo/tag...")
            search_terms = [
                f"genre:\"{genre}\"",  # Busca exata no gênero
                f"tag:{genre}",
                f"{genre} playlist",
                f"{genre} mix",
                genre
            ]
            
            for term in search_terms:
                if len(genre_tracks) >= tracks_per_genre: break
                
                offset = 0
                # Limite menor por termo para variar mais
                while offset < 100 and len(genre_tracks) < tracks_per_genre:
                    try:
                        results = self.sp.search(q=term, type='track', limit=SEARCH_LIMIT, offset=offset)
                        items = results.get('tracks', {}).get('items', [])
                        if not items: break
                        
                        for track in items:
                            if track.get('uri'): genre_tracks.add(track['uri'])
                            
                        offset += SEARCH_LIMIT
                        self.smart_sleep()
                    except Exception as e: 
                        print(f"     ⚠️ Erro na busca '{term}': {e}")
                        break
            
            print(f"   ✅ Total para '{genre}': {len(genre_tracks)} músicas")
            track_uris.update(genre_tracks)
            self.smart_sleep()

        
        # Estratégia 3: Buscar playlists do gênero e extrair músicas (Iterar por todos os gêneros)
        print("  📋 Buscando em playlists de usuários...")
        
        for genre in genres_list:
            if len(track_uris) >= target_count: break
            
            try:
                playlist_results = self.sp.search(q=genre, type='playlist', limit=5) # Limite reduzido
                self.smart_sleep()
                
                for playlist in playlist_results.get('playlists', {}).get('items', []):
                    if len(track_uris) >= target_count: break
                    if playlist and playlist.get('id'):
                        try:
                            # Reduzido para pegar menos músicas por playlist (mais variedade, menos chance de erro)
                            playlist_tracks = self.sp.playlist_tracks(playlist['id'], limit=30)
                            for item in playlist_tracks.get('items', []):
                                track = item.get('track')
                                if track and track.get('uri') and not track['uri'].startswith('spotify:local:'):
                                    track_uris.add(track['uri'])
                            
                            self.smart_sleep()
                        except Exception: continue
            except Exception: pass
        
        print(f"\n✅ Total de músicas únicas encontradas: {len(track_uris)}")
        
        # Converter para lista e limitar ao target
        track_list = list(track_uris)
        random.shuffle(track_list)  # Embaralhar para variedade
        
        return track_list[:target_count]
    
    def create_playlist(self, genres_list, track_count, vol_num=1, total_vols=1):
        """Cria uma nova playlist (com suporte a volumes)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Nome da playlist baseado nos primeiros gêneros
        title_genres = ", ".join(genres_list[:2]).title()
        if len(genres_list) > 2:
            title_genres += " & More"
            
        name = f"🎵 {title_genres} Mix"
        if total_vols > 1:
            name += f" - Vol. {vol_num}/{total_vols}"
        
        description = f"Super Mix gerado com: {', '.join(genres_list)}. {track_count} músicas. Criado em {timestamp}."
        if total_vols > 1:
            description += f" (Parte {vol_num} de {total_vols})"
        
        try:
            playlist = self.sp.user_playlist_create(
                user=self.user_id,
                name=name,
                public=True,
                description=description
            )
            
            print(f"\n✅ Playlist criada: '{name}'")
            return playlist['id'], playlist['external_urls']['spotify']
            
        except Exception as e:
            print(f"❌ Erro ao criar playlist: {e}")
            return None, None
    
    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Adiciona músicas à playlist em lotes"""
        print(f"\n📥 Adicionando {len(track_uris)} músicas à playlist...")
        
        added = 0
        failed = 0
        
        # Adicionar em lotes de 100 (limite da API)
        for i in range(0, len(track_uris), TRACKS_PER_REQUEST):
            batch = track_uris[i:i + TRACKS_PER_REQUEST]
            
            try:
                self.sp.playlist_add_items(playlist_id, batch)
                added += len(batch)
                
                # Mostrar progresso
                progress = (added / len(track_uris)) * 100
                bar_length = 30
                filled = int(bar_length * added / len(track_uris))
                bar = "█" * filled + "░" * (bar_length - filled)
                
                print(f"\r  [{bar}] {progress:.1f}% ({added}/{len(track_uris)})", end="", flush=True)
                
                self.smart_sleep()
                
            except Exception as e:
                failed += len(batch)
                print(f"\n  ⚠️ Erro ao adicionar lote: {e}")
        
        print(f"\n\n✅ Adicionadas: {added} músicas")
        if failed > 0:
            print(f"⚠️ Falhas: {failed} músicas")
        
        return added
    
    def run(self):
        """Executa o programa principal"""
        print("=" * 60)
        print("  🎵 SPOTIFY MEGA MIXER")
        print("  Crie coleções gigantes (nós dividimos em volumes para você!)")
        print("=" * 60)
        
        # Autenticar
        if not self.authenticate():
            return
        
        while True:
            # Obter lista de gêneros
            genres = self.get_genres_input()
            
            # Obter quantidade
            track_count = self.get_track_count()
            
            print(f"\n📋 Resumo:")
            print(f"  • Estilos: {', '.join(genres)}")
            print(f"  • Músicas Totais: {track_count}")
            
            # Calcular volumes
            total_vols = (track_count // PLAYLIST_LIMIT) + (1 if track_count % PLAYLIST_LIMIT > 0 else 0)
            if total_vols > 1:
                print(f"  • Volumes necessários: {total_vols} playlists")
            
            confirm = input("\n🚀 Confirmar e iniciar? (s/n): ").strip().lower()
            if confirm != 's':
                print("❌ Operação cancelada")
                continue
            
            # Buscar músicas (Busca única para garantir variedade global)
            start_time = time.time()
            all_tracks = self.search_tracks_by_keywords(genres, track_count)
            
            if not all_tracks:
                print("❌ Nenhuma música encontrada.")
                continue
            
            total_found = len(all_tracks)
            
            # Dividir em volumes de 10.000
            for i in range(0, total_found, PLAYLIST_LIMIT):
                vol_tracks = all_tracks[i : i + PLAYLIST_LIMIT]
                vol_num = (i // PLAYLIST_LIMIT) + 1
                
                print(f"\n💿 Processando Volume {vol_num}/{total_vols} ({len(vol_tracks)} músicas)...")
                
                # Criar playlist do volume atual
                playlist_id, playlist_url = self.create_playlist(genres, len(vol_tracks), vol_num, total_vols)
                
                if not playlist_id:
                    continue
                
                # Adicionar músicas
                self.add_tracks_to_playlist(playlist_id, vol_tracks)
                print(f"   🔗 Link do Vol. {vol_num}: {playlist_url}")
            
            # Resumo final
            elapsed = time.time() - start_time
            print("\n" + "=" * 60)
            print("  ✅ COLEÇÃO CONCLUÍDA!")
            print("=" * 60)
            print(f"  • Total adicionado: {total_found} músicas")
            print(f"  • Volumes criados: {total_vols}")
            print(f"  • Tempo total: {elapsed:.1f} segundos")
            print("=" * 60)
            
            # Continuar?
            again = input("\n🔄 Criar outra coleção? (s/n): ").strip().lower()
            if again != 's':
                print("\n👋 Obrigado por usar o Spotify Playlist Filler!")
                break


if __name__ == "__main__":
    filler = SpotifyPlaylistFiller()
    filler.run()
