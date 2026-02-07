from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import time
import re # Added for text filtering
from datetime import datetime
import os

app = FastAPI()

# Enable CORS for React frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# CONSTANTS & CONFIG
# ==========================================
MAX_TRACKS = 100000
PLAYLIST_LIMIT = 10000
TRACKS_PER_REQUEST = 50
SEARCH_LIMIT = 20
SAFE_MODE_DELAY = 1  # Seconds to sleep between calls

AVAILABLE_GENRES = [
    "acoustic", "alt-rock", "alternative", "alternative-metal", "ambient",
    "black-metal", "bluegrass", "blues", "breakbeat",
    "british", "chicago-house", "children", "chill", "classical",
    "club", "comedy", "country", "dance", "dancehall", "death-metal", "deep-house",
    "detroit-techno", "disco", "disney", "drum-and-bass", "dub", "dubstep", "edm",
    "electro", "electronic", "emo", "emotional", "folk", "funk", "garage",
    "gospel", "goth", "grindcore", "groove", "grunge", "guitar",
    "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal", "hip-hop",
    "industrial", "jazz",
    "kids", "metal", "metal-misc",
    "metalcore", "minimal-techno", "movies", "new-age", "new-release",
    "opera", "party", "piano", "pop", "pop-film",
    "post-dubstep", "power-pop", "progressive-house", "progressive-metalcore", "psych-rock", "punk",
    "punk-rock", "r-n-b", "rainy-day", "reggae", "road-trip",
    "rock", "rock-n-roll", "rockabilly", "romance", "sad", 
    "show-tunes", "singer-songwriter", "ska", "sleep", "songwriter",
    "soundtracks", "study", "summer", "synth-pop",
    "techno", "trance", "trip-hop", "work-out",

    # VIRAL / MODERN / SUBGENRES (Added by Request)
    "amapiano", "bedroom-pop", "city-pop", "cyberpunk", "dark-synth", "drift-phonk", 
    "drill", "dream-pop", "eurovision", "future-bass", "future-funk", "glitch-core", 
    "hardwave", "hyperpop", "jersey-club", "kawaii-metal", "liquid-dnb", "lo-fi", 
    "math-rock", "melodic-techno", "phonk", "rage", "retrowave", "shoegaze", 
    "slowed-reverb", "synthwave", "uk-drill", "vaporwave", 
    "witch-house", "y2k"
]

# ==========================================
# MODELS
# ==========================================
class TokenRequest(BaseModel):
    token: str

class ExecuteRequest(BaseModel):
    token: str
    genres: List[str]
    playlist_name: Optional[str] = None
    description: Optional[str] = None
    track_count: int

# ==========================================
# HELPER FUNCTIONS (LOGIC MIGRATED FROM APP.PY)
# ==========================================
def smart_sleep():
    time.sleep(random.uniform(1, 3))

def is_safe_text(text, genre=None):
    """
    Filters out text containing non-Latin scripts (Cyrillic, CJK, etc)
    UNLESS the genre specifically allows it (e.g. K-Pop, J-Pop).
    """
    if not text: return True
    
    # 1. Check Exemptions for Specific Genres
    exempt_genres = [
        "k-pop", "j-pop", "j-rock", "j-idol", "j-dance", "anime", 
        "latin", "latino", "reggaeton", "salsa", "tango", "world-music"
    ]
    if genre and genre in exempt_genres:
        return True # Allow native script for these genres
        
    # 2. Enforce Latin-Only for general genres (Pop, Rock, etc)
    # Reject Cyrillic (Russian/Ukrainian)
    if re.search(r'[\u0400-\u04FF]', text): return False 
    # Reject CJK (Chinese/Japanese/Korean) if not exempt
    if re.search(r'[\u4e00-\u9fff]', text): return False 
    if re.search(r'[\u3040-\u30ff]', text): return False 
    if re.search(r'[\uac00-\ud7af]', text): return False
    # Reject Arabic/Hebrew/etc
    if re.search(r'[\u0600-\u06FF]', text): return False
    
    return True

def search_tracks_logic(sp, genres, target_count):
    track_uris = set()
    tracks_per_genre = int(target_count / len(genres)) + 1
    
    print(f"Starting search for: {genres}")
    
    for genre in genres:
        genre_tracks = set()
        print(f"Processing genre: {genre}")
        
        # Strategy 1: Recommendations
        if genre in AVAILABLE_GENRES:
            try:
                results = sp.recommendations(seed_genres=[genre], limit=TRACKS_PER_REQUEST, min_popularity=0, market='US')
                for track in results.get('tracks', []):
                    # Filter: Must not have Cyrillic/Russian text in name or artist
                    t_name = track.get('name', '')
                    a_name = track['artists'][0]['name'] if track.get('artists') else ''
                    
                    if track.get('uri') and is_safe_text(t_name, genre) and is_safe_text(a_name, genre):
                         genre_tracks.add(track['uri'])
                smart_sleep()
            except Exception as e:
                print(f"Rec Error: {e}")

        # Strategy 2: Strict Search (Deep Dive using 'genre:' tag only)
        # We removed broad terms like "mix" or raw strings to prevent genre pollution.
        search_terms = [f"genre:\"{genre}\""]
        
        for term in search_terms:
            if len(genre_tracks) >= tracks_per_genre: break
            
            offset = 0
            # Sudo-Infinite Search: Increased limit from 100 to 950 to find more valid tracks
            while offset < 950 and len(genre_tracks) < tracks_per_genre:
                try:
                    results = sp.search(q=term, type='track', limit=SEARCH_LIMIT, offset=offset, market='US')
                    items = results.get('tracks', {}).get('items', [])
                    if not items: break
                    
                    for track in items:
                         # Filter: Must not have Cyrillic/Russian text in name or artist
                        t_name = track.get('name', '')
                        a_name = track['artists'][0]['name'] if track.get('artists') else ''
                        if track.get('uri') and is_safe_text(t_name, genre) and is_safe_text(a_name, genre):
                            genre_tracks.add(track['uri'])
                    
                    offset += SEARCH_LIMIT
                    smart_sleep()
                    
                    if len(genre_tracks) >= tracks_per_genre: break
                except Exception: break
        
        track_uris.update(genre_tracks)
    
    # Strategy 3 (Fallback) REMOVED to prevent contaminating playlist with other genres.
    # We now rely exclusively on Recommendations and Strict Genre Search.

    track_list = list(track_uris)
    random.shuffle(track_list)
    return track_list[:target_count]

def create_playlists_logic(sp, user_id, genres, all_tracks, base_name, base_desc):
    total_found = len(all_tracks)
    if total_found == 0:
        return []

    links = []
    
    # Calculate volumes
    total_vols = (total_found // PLAYLIST_LIMIT) + (1 if total_found % PLAYLIST_LIMIT > 0 else 0)
    
    for i in range(0, total_found, PLAYLIST_LIMIT):
        vol_tracks = all_tracks[i : i + PLAYLIST_LIMIT]
        vol_num = (i // PLAYLIST_LIMIT) + 1
        
        # Name formatting
        name = base_name
        if not name or name.strip() == "":
            title_genres = ", ".join(genres[:2]).title()
            if len(genres) > 2: title_genres += " & More"
            name = f"🎵 {title_genres} Mix"
            
        if total_vols > 1: name += f" - Vol. {vol_num}/{total_vols}"
        
        desc = base_desc
        if not desc or desc.strip() == "":
            desc = f"Generated with {', '.join(genres)}. {len(vol_tracks)} tracks."
        if total_vols > 1: desc += f" (Part {vol_num}/{total_vols})"
        
        try:
            # Create
            playlist = sp.user_playlist_create(user=user_id, name=name, public=True, description=desc)
            playlist_id = playlist['id']
            playlist_url = playlist['external_urls']['spotify']
            links.append({"name": name, "url": playlist_url})
            
            # Add Tracks
            for j in range(0, len(vol_tracks), TRACKS_PER_REQUEST):
                batch = vol_tracks[j:j + TRACKS_PER_REQUEST]
                try:
                    sp.playlist_add_items(playlist_id, batch)
                    smart_sleep()
                except Exception as e:
                    print(f"Error adding batch: {e}")
                    
        except Exception as e:
            print(f"Critical error creating playlist: {e}")
            raise e
            
    return links

# ==========================================
# ERROR HANDLING
# ==========================================
def handle_spotify_error(e):
    if hasattr(e, 'http_status'):
        status = e.http_status
        
        if status == 400:
             return {
                "status": "bad_request",
                "message": "⚠️ Solicitação inválida. Verifique se o token tem as permissões corretas."
            }
        elif status == 401:
            return {
                "status": "auth_error",
                "message": "🔒 Token inválido ou expirado. Por favor, gere um novo token no Developer Console."
            }
        elif status == 403:
             return {
                "status": "forbidden",
                "message": "🚫 Acesso negado. Seu token não tem permissão para criar playlists (playlist-modify-public/private)."
            }
        elif status == 404:
             return {
                "status": "not_found",
                "message": "❓ Recurso não encontrado no Spotify."
            }
        elif status == 429:
            retry_after = int(e.headers.get("Retry-After", 5)) if hasattr(e, 'headers') else 5
            return {
                "status": "rate_limit",
                "message": f"⏳ Limite de taxa excedido (Rate Limit). O Spotify bloqueou temporariamente. Espere {retry_after}s.",
                "retry_after": retry_after
            }
        elif status >= 500:
             return {
                "status": "server_error",
                "message": "🔥 Erro nos servidores do Spotify. Tente novamente mais tarde."
            }
            
    # Generic Catch-All
    return {
        "status": "error",
        "message": f"Erro inesperado: {str(e)}"
    }

# ==========================================
# ENDPOINTS
# ==========================================
@app.get("/")
def read_root():
    return {"status": "Spotify Mega Mixer API is running"}

@app.get("/genres")
def get_genres():
    return {"genres": sorted(AVAILABLE_GENRES)}

@app.post("/authenticate")
def authenticate(req: TokenRequest):
    try:
        # Token Cleanup
        clean_token = req.token
        if "Bearer" in clean_token:
            clean_token = clean_token.split("Bearer")[-1]
        clean_token = clean_token.replace("'", "").replace('"', "").replace("\\", "").strip()

        sp = spotipy.Spotify(auth=clean_token)
        user = sp.current_user()
        return {
            "status": "success", 
            "user": user['display_name'], 
            "id": user['id'], 
            "image": user['images'][0]['url'] if user['images'] else None,
            "cleaned_token": clean_token # Send back cleaned token for future use
        }
    except Exception as e:
        return handle_spotify_error(e)

@app.post("/execute")
def execute(req: ExecuteRequest):
    try:
        sp = spotipy.Spotify(auth=req.token, requests_timeout=10, status_retries=0)
        user = sp.current_user()
        user_id = user['id']
        
        # 1. Search
        print("Step 1: Searching...")
        tracks = search_tracks_logic(sp, req.genres, req.track_count)
        
        if not tracks:
            return {"status": "error", "message": "No tracks found for these genres."}
            
        # 2. Create
        print("Step 2: Creating...")
        links = create_playlists_logic(sp, user_id, req.genres, tracks, req.playlist_name, req.description)
        
        return {"status": "success", "links": links, "total_tracks": len(tracks)}
        
    except Exception as e:
        return handle_spotify_error(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
