"""
=============================================================================
ETERNO DEV PROFILE - MASTER SYNC & CARD GENERATOR
Sincronización dinámica de vídeos de YouTube y videojuegos de Itch.io
=============================================================================
Funcionalidades:
1. Conexión directa a las APIs oficiales con GitHub Secrets:
   - ITCH_API_KEY: Consulta https://api.itch.io/profile/games
   - YOUTUBE_API_KEY: Consulta YouTube Data API v3
2. Fallback resiliente: Si no hay claves o falla la API, consulta
   los datos en vivo de games.json y videos.json de EternoDev-Official.
3. Descarga y almacenamiento en caché de miniaturas e imágenes de portada.
4. Renderizado vectorial en SVG de:
   - yt_badge.svg & yt_card_*.svg (Vídeos de YouTube)
   - itch_badge.svg & itch_card_*.svg (Videojuegos de Itch.io)
5. Reescritura dinámica de README.md si se agregan nuevos vídeos o juegos.
=============================================================================
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error
import re
from datetime import datetime

# Rutas del repositorio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SVG_DIR = os.path.join(ASSETS_DIR, "svg")
THUMB_DIR = os.path.join(ASSETS_DIR, "thumbnail")
ITCH_THUMB_DIR = os.path.join(THUMB_DIR, "itch")
README_PATH = os.path.join(BASE_DIR, "README.md")

os.makedirs(SVG_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)
os.makedirs(ITCH_THUMB_DIR, exist_ok=True)

# Path vectorial oficial de Itch.io
ITCH_ICON_PATH = "M 16 5 C 12.748 5 8.3121094 5.0508594 7.4121094 5.1308594 C 6.4021094 5.7368594 4.4028125 8.0309531 4.3828125 8.6269531 L 4.3828125 9.6269531 C 4.3828125 10.889953 5.5657188 12 6.6367188 12 C 7.9197187 12 8.9902344 10.929969 8.9902344 9.6679688 C 8.9902344 10.929969 10.0305 12 11.3125 12 C 12.6055 12 13.605469 10.930969 13.605469 9.6679688 C 13.605469 10.929969 14.695281 12 15.988281 12 L 16.009766 12 C 17.302766 12 18.392578 10.930969 18.392578 9.6679688 C 18.392578 10.929969 19.402547 12 20.685547 12 C 21.968547 12 23.009766 10.930969 23.009766 9.6679688 C 23.009766 10.929969 24.080281 12 25.363281 12 C 26.434281 12 27.615234 10.889953 27.615234 9.6269531 L 27.615234 8.6269531 C 27.595234 8.0309531 25.595938 5.7368594 24.585938 5.1308594 C 21.443938 5.0198594 19.252 5 16 5 z M 13.550781 11.742188 C 12.497781 13.552188 9.8523125 13.573906 8.8203125 11.753906 C 8.1903125 12.845906 6.7642969 13.267547 6.1542969 13.060547 C 5.9762969 14.959547 5.8534844 24.70875 7.1464844 26.34375 C 10.943484 27.22875 21.164516 27.20975 24.853516 26.34375 C 26.348516 24.81975 26.013703 14.821547 25.845703 13.060547 C 25.235703 13.267547 23.809453 12.845906 23.189453 11.753906 C 22.146453 13.573906 19.501219 13.552188 18.449219 11.742188 C 18.124219 12.332187 17.367 13.109375 16 13.109375 C 14.997 13.148375 14.051781 12.607187 13.550781 11.742188 z M 11.419922 14 C 12.219922 14 12.950078 14.000469 13.830078 14.980469 C 15.280078 14.830469 16.719922 14.830469 18.169922 14.980469 C 19.059922 14.010469 19.780078 14.009766 20.580078 14.009766 C 23.160078 14.009766 23.780937 17.819609 24.710938 21.099609 C 25.550938 24.149609 24.429062 24.230469 23.039062 24.230469 C 20.969062 24.150469 19.820313 22.650625 19.820312 21.140625 C 17.890313 21.460625 14.809688 21.580625 12.179688 21.140625 C 12.179688 22.650625 11.030938 24.150469 8.9609375 24.230469 C 7.5709375 24.230469 6.4490625 24.149609 7.2890625 21.099609 C 8.2190625 17.799609 8.8399219 14.009766 11.419922 14.009766 L 11.419922 14 z M 16 16.876953 C 16 16.876953 14.306 18.439375 14 18.984375 L 15.107422 18.943359 L 15.107422 19.910156 C 15.107422 19.968156 15.926 19.917969 16 19.917969 C 16.447 19.934969 16.892578 19.951156 16.892578 19.910156 L 16.892578 18.943359 L 18 18.984375 C 17.694 18.438375 16 16.876953 16 16.876953 z"

# Iconos de plataforma en SVG
PLAT_ICONS = {
    "windows": '<g title="Windows" fill="#00A4EF"><path d="M0 2.2L6.3 1.3V7.2H0V2.2ZM0 7.8H6.3V13.7L0 12.8V7.8ZM6.9 1.2L15 0V7.2H6.9V1.2ZM6.9 7.8H15V15L6.9 13.8V7.8Z"/></g>',
    "linux": '<g title="Linux" fill="#FCC624"><circle cx="7.5" cy="7.5" r="7" fill="#E95420"/><path d="M7.5 2C5.5 2 4.5 4 4.5 6C4.5 7.5 5 8.5 5 10C4 11 3.5 12 3.5 13C4.5 13.5 6 13 7.5 13C9 13 10.5 13.5 11.5 13C11.5 12 11 11 10 10C10 8.5 10.5 7.5 10.5 6C10.5 4 9.5 2 7.5 2Z" fill="#FFFFFF"/></g>',
    "osx": '<g title="macOS" fill="#AAAAAA"><path d="M12.5 7.8C12.5 5.5 14.3 4.4 14.4 4.3C13.3 2.7 11.7 2.5 11.1 2.4C9.7 2.3 8.3 3.3 7.6 3.3C6.8 3.3 5.7 2.4 4.6 2.4C3.1 2.5 1.7 3.3 1 4.6C-0.5 7.2 0.6 11 2.1 13.1C2.8 14.1 3.7 15.3 4.8 15.2C5.9 15.2 6.3 14.5 7.6 14.5C8.9 14.5 9.3 15.2 10.4 15.2C11.6 15.2 12.4 14.1 13.1 13.1C13.9 11.9 14.3 10.8 14.4 10.7C14.3 10.6 12.5 9.9 12.5 7.8ZM10.2 1.6C10.7 1 11.1 0.1 11 0C10.2 0 9.2 0.5 8.7 1.1C8.2 1.6 7.8 2.5 7.9 3.3C8.8 3.4 9.7 2.2 10.2 1.6Z"/></g>',
    "web": '<g title="Web" fill="#FA5C5C"><circle cx="7.5" cy="7.5" r="7" stroke="#FA5C5C" stroke-width="1.4" fill="none"/><ellipse cx="7.5" cy="7.5" rx="3.5" ry="7" stroke="#FA5C5C" stroke-width="1.4" fill="none"/><line x1="0.5" y1="7.5" x2="14.5" y2="7.5" stroke="#FA5C5C" stroke-width="1.4"/></g>'
}

def fetch_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error consultando {url}: {e}")
        return None

def download_file(url, target_path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp, open(target_path, 'wb') as f:
            f.write(resp.read())
        return True
    except Exception as e:
        print(f"Error descargando {url}: {e}")
        return False

# =============================================================================
# 1. SINCRONIZACIÓN DE ITCH.IO
# =============================================================================
def get_itch_games():
    api_key = os.environ.get("ITCH_API_KEY")
    games = []
    
    if api_key:
        print("[+] Consultando Itch.io API oficial...")
        data = fetch_json("https://api.itch.io/profile/games", headers={'Authorization': f'Bearer {api_key}'})
        if data and "games" in data:
            for g in data["games"]:
                if g.get("published") is not False:
                    slug = (g.get("url") or "").rstrip("/").split("/")[-1]
                    games.append({
                        "id": g.get("id"),
                        "title": g.get("title"),
                        "url": g.get("url"),
                        "cover_url": g.get("cover_url"),
                        "slug": slug,
                        "desc": g.get("short_text") or "Videojuego indie en Itch.io",
                        "p_windows": bool(g.get("p_windows")),
                        "p_linux": bool(g.get("p_linux")),
                        "p_osx": bool(g.get("p_osx")),
                        "p_browser": g.get("type") == "html"
                    })
    
    # Fallback a games.json de EternoDev-Official si la API no está configurada
    if not games:
        print("[*] Usando fuente en vivo de games.json...")
        raw_games = fetch_json("https://raw.githubusercontent.com/paucg06/EternoDev-Official/main/games.json")
        if raw_games:
            for g in raw_games:
                slug = (g.get("url") or "").rstrip("/").split("/")[-1]
                games.append({
                    "id": g.get("id"),
                    "title": g.get("title"),
                    "url": g.get("url"),
                    "cover_url": g.get("cover_url"),
                    "slug": slug,
                    "genre": g.get("genre") or "Videojuego",
                    "desc": g.get("short_text") or "Videojuego indie en Itch.io",
                    "p_windows": bool(g.get("p_windows")),
                    "p_linux": bool(g.get("p_linux")),
                    "p_osx": bool(g.get("p_osx")),
                    "p_browser": bool(g.get("p_browser"))
                })
                
    # Enriquecer géneros y badges conocidos
    genre_map = {
        "castlecat-rpg": ("Aventura / RPG", "JUGAR EN WEB", ["web"]),
        "oonga-bunga": ("Lucha / Party Game", "DESCARGAR PC", ["windows", "linux"]),
        "soap-dodger": ("Acción / Bullet Hell", "PC & WEB", ["windows", "linux", "osx", "web"]),
        "space-blitz": ("Shooter Arcade", "JUGAR EN WEB", ["web"]),
        "verdades-incompletas": ("Novela Visual", "PC & WEB", ["windows", "linux", "osx", "web"])
    }
    
    for g in games:
        slug = g.get("slug", "")
        if slug in genre_map:
            genre, badge, plats = genre_map[slug]
            g["genre"] = genre
            g["badge"] = badge
            g["platforms"] = plats
        else:
            plats = []
            if g.get("p_windows"): plats.append("windows")
            if g.get("p_linux"): plats.append("linux")
            if g.get("p_osx"): plats.append("osx")
            if g.get("p_browser"): plats.append("web")
            g["platforms"] = plats or ["web"]
            g["genre"] = g.get("genre", "Videojuego")
            g["badge"] = "JUGAR EN ITCH.IO"
            
    return games

def render_itch_cards(games):
    for idx, game in enumerate(games[:5], start=1):
        slug = game.get("slug") or f"game_{idx}"
        img_name = f"{slug.replace('-', '_')}.png"
        img_path = os.path.join(ITCH_THUMB_DIR, img_name)
        
        if not os.path.exists(img_path) and game.get("cover_url"):
            print(f"Descargando portada de {game['title']}...")
            download_file(game["cover_url"], img_path)
            
        b64_img = ""
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                b64_img = base64.b64encode(f.read()).decode("utf-8")

        # Iconos de plataformas
        plat_items = []
        x_off = 0
        for p in game["platforms"]:
            if p in PLAT_ICONS:
                plat_items.append(f'<g transform="translate({x_off}, 0) scale(0.9)">{PLAT_ICONS[p]}</g>')
                x_off += 20
        plat_svg = "".join(plat_items)

        w, h = 580, 445
        badge_text = game.get("badge", "JUGAR")
        badge_w = len(badge_text) * 8 + 18
        badge_x = w - badge_w - 14

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <clipPath id="itchClip_{idx}">
      <rect x="0" y="0" width="{w}" height="326" rx="14"/>
    </clipPath>
    <linearGradient id="itchGrad_{idx}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#000000" stop-opacity="0.0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.6"/>
    </linearGradient>
    <style>
      .itch-game-title {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 20px;
        fill: #FFFFFF;
      }}
      .itch-game-genre {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 14px;
        fill: #FA5C5C;
      }}
      .itch-game-desc {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 400;
        font-size: 13.5px;
        fill: #AAAAAA;
      }}
      .itch-badge-text {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 11.5px;
        fill: #FFFFFF;
        letter-spacing: 0.5px;
      }}
    </style>
  </defs>

  <rect width="{w}" height="{h}" fill="#0F0F0F" rx="16"/>

  <g clip-path="url(#itchClip_{idx})">
    <image href="data:image/png;base64,{b64_img}" 
           x="0" y="0" width="{w}" height="326" 
           preserveAspectRatio="xMidYMid slice"/>
    <rect x="0" y="240" width="{w}" height="86" fill="url(#itchGrad_{idx})"/>
    <rect x="{badge_x}" y="290" width="{badge_w}" height="24" rx="6" fill="#18181B" fill-opacity="0.9" stroke="#FA5C5C" stroke-width="1.2"/>
    <text x="{badge_x + badge_w / 2}" y="306" text-anchor="middle" class="itch-badge-text">{badge_text}</text>
  </g>

  <g transform="translate(14, 342)">
    <circle cx="21" cy="21" r="21" fill="#1E1E24" stroke="#FA5C5C" stroke-width="1.5"/>
    <g transform="translate(9, 9) scale(0.75)" fill="#FA5C5C">
      <path d="{ITCH_ICON_PATH}"/>
    </g>

    <g transform="translate(58, 8)">
      <text x="0" y="8" class="itch-game-title">{game["title"]}</text>
      <g transform="translate(0, 30)">
        <text x="0" y="0" class="itch-game-genre">{game["genre"]}</text>
        <g transform="translate(180, -11)">
          {plat_svg}
        </g>
      </g>
      <text x="0" y="52" class="itch-game-desc">{game["desc"]}</text>
    </g>

    <g transform="translate({w - 60}, 12)">
      <rect x="0" y="0" width="34" height="34" rx="17" fill="#1E1E24" stroke="#33333E" stroke-width="1"/>
      <polygon points="13,10 24,17 13,24" fill="#FA5C5C"/>
    </g>
  </g>
</svg>'''
        card_path = os.path.join(SVG_DIR, f"itch_card_{idx}.svg")
        with open(card_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"[OK] Tarjeta Itch.io {idx} generada: {game['title']}")

    # Tarjeta 6 de Catálogo Completo
    w, h = 580, 445
    card_6 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <clipPath id="itchCatalogClip">
      <rect x="0" y="0" width="{w}" height="326" rx="14"/>
    </clipPath>
    <linearGradient id="catalogGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2D1517"/>
      <stop offset="50%" stop-color="#1E1E24"/>
      <stop offset="100%" stop-color="#141419"/>
    </linearGradient>
    <style>
      .catalog-main-title {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 800;
        font-size: 26px;
        fill: #FFFFFF;
      }}
      .catalog-sub {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 15px;
        fill: #FA5C5C;
      }}
      .catalog-desc {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 400;
        font-size: 13.5px;
        fill: #AAAAAA;
      }}
      .btn-text {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 14px;
        fill: #FFFFFF;
      }}
    </style>
  </defs>

  <rect width="{w}" height="{h}" fill="#0F0F0F" rx="16"/>

  <g clip-path="url(#itchCatalogClip)">
    <rect width="{w}" height="326" fill="url(#catalogGrad)"/>
    <circle cx="290" cy="140" r="110" fill="#FA5C5C" fill-opacity="0.08"/>
    <circle cx="290" cy="140" r="70" fill="#FA5C5C" fill-opacity="0.12"/>
    <g transform="translate(258, 80) scale(2.0)" fill="#FA5C5C">
      <path d="{ITCH_ICON_PATH}"/>
    </g>
    <text x="290" y="195" text-anchor="middle" class="catalog-main-title">EternoDev en Itch.io</text>
    <text x="290" y="225" text-anchor="middle" class="catalog-sub">Catálogo Completo de Videojuegos Indie</text>
    <g transform="translate(200, 255)">
      <rect width="180" height="38" rx="19" fill="#FA5C5C"/>
      <text x="90" y="24" text-anchor="middle" class="btn-text">Ver todos los juegos →</text>
    </g>
  </g>

  <g transform="translate(14, 342)">
    <circle cx="21" cy="21" r="21" fill="#FA5C5C"/>
    <g transform="translate(9, 9) scale(0.75)" fill="#FFFFFF">
      <path d="{ITCH_ICON_PATH}"/>
    </g>
    <g transform="translate(58, 8)">
      <text x="0" y="8" class="catalog-sub" style="font-size: 19px; fill: #FFFFFF;">Explorar perfil de creador</text>
      <text x="0" y="30" class="catalog-sub">eternodev.itch.io</text>
      <text x="0" y="52" class="catalog-desc">5+ juegos publicados • Nuevos proyectos en desarrollo</text>
    </g>
    <g transform="translate({w - 60}, 12)">
      <rect x="0" y="0" width="34" height="34" rx="17" fill="#FA5C5C"/>
      <polygon points="13,10 24,17 13,24" fill="#FFFFFF"/>
    </g>
  </g>
</svg>'''
    with open(os.path.join(SVG_DIR, "itch_card_6.svg"), "w", encoding="utf-8") as f:
        f.write(card_6)
    print("[OK] Tarjeta Itch.io 6 (Catálogo) generada.")

# =============================================================================
# 2. SINCRONIZACIÓN DE YOUTUBE
# =============================================================================
def wrap_youtube_title(title, max_chars=34):
    words = title.split()
    line1, line2 = [], []
    curr_len = 0
    for w in words:
        if not line2:
            needed = len(w) + (1 if line1 else 0)
            if curr_len + needed <= max_chars:
                line1.append(w)
                curr_len += needed
            else:
                line2.append(w)
                curr_len = len(w)
        else:
            needed = len(w) + 1
            if curr_len + needed <= max_chars:
                line2.append(w)
                curr_len += needed
            else:
                line2_str = " ".join(line2)
                if not line2_str.endswith("..."):
                    if len(line2_str) <= max_chars - 3:
                        line2.append("...")
                    else:
                        line2[-1] = line2[-1][:max(1, max_chars - 4)] + "..."
                break
    return " ".join(line1), " ".join(line2)

def get_youtube_videos():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    channel_id = "UCewJv1M1YAKfLcbld6iWxWg"
    videos = []

    # Vídeos estáticos de base
    base_videos = [
        {
            "id": "wjoGjOxCTCQ",
            "title": "¡REHICE el Juego de mis SUEÑOS! - DevBlog 2",
            "thumb_file": "thumb_rehice.png",
            "duration": "14:14",
            "views": "153 visualizaciones • 12 ene 2025"
        },
        {
            "id": "DFR5UtAuHTw",
            "title": "Sobreviví a mi PRIMERA GameJam",
            "thumb_file": "thumb_gamejam.png",
            "duration": "10:02",
            "views": "18 visualizaciones • 9 jun 2025"
        },
        {
            "id": "bRbhRWQvqs8",
            "title": "Hice un VTUBER en 48 HORAS",
            "thumb_file": "thumb_vtuber.png",
            "duration": "10:10",
            "views": "167 visualizaciones • 20 abr 2025"
        },
        {
            "id": "F1-R5hIjGLM",
            "title": "¡Creando Mi Propio ROGUELIKE Desde CERO!- DevBlog 1",
            "thumb_file": "thumb_roguelike.png",
            "duration": "20:00",
            "views": "230 visualizaciones • 22 nov 2024"
        }
    ]

    if api_key:
        print("[+] Consultando YouTube Data API v3 oficial...")
        chan_data = fetch_json(f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}")
        uploads_id = chan_data.get("items", [{}])[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads") if chan_data else None
        if uploads_id:
            items_data = fetch_json(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_id}&maxResults=6&key={api_key}")
            if items_data and "items" in items_data:
                vids_ids = [i["snippet"]["resourceId"]["videoId"] for i in items_data["items"] if "snippet" in i]
                if vids_ids:
                    stats_data = fetch_json(f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(vids_ids)}&key={api_key}")
                    if stats_data and "items" in stats_data:
                        for item in stats_data["items"]:
                            v_id = item["id"]
                            s = item["snippet"]
                            v_views = item.get("statistics", {}).get("viewCount", "0")
                            videos.append({
                                "id": v_id,
                                "title": s["title"],
                                "thumb_url": s.get("thumbnails", {}).get("maxres", {}).get("url") or f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg",
                                "views": f"{v_views} visualizaciones",
                                "duration": "10:00"
                            })

    return videos if len(videos) >= 4 else base_videos

def render_youtube_cards(videos):
    logo_path = os.path.join(THUMB_DIR, "logo.png")
    b64_avatar = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64_avatar = base64.b64encode(f.read()).decode("utf-8")

    w, h = 580, 445
    check_path = "M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.4-1.4 3.6 3.6 7.6-7.6L19 8l-9 9z"

    for idx, video in enumerate(videos[:4], start=1):
        thumb_file = video.get("thumb_file", f"thumb_{video['id']}.jpg")
        thumb_path = os.path.join(THUMB_DIR, thumb_file)
        
        if not os.path.exists(thumb_path) and video.get("thumb_url"):
            download_file(video["thumb_url"], thumb_path)
            
        b64_thumb = ""
        mime = "png" if thumb_file.endswith(".png") else "jpeg"
        if os.path.exists(thumb_path):
            with open(thumb_path, "rb") as f:
                b64_thumb = base64.b64encode(f.read()).decode("utf-8")

        line1, line2 = wrap_youtube_title(video["title"], max_chars=35)
        if line2:
            title_svg = f'''<text x="0" y="0" class="yt-title">{line1}</text>
      <text x="0" y="24" class="yt-title">{line2}</text>'''
            channel_y, meta_y = 48, 68
        else:
            title_svg = f'''<text x="0" y="0" class="yt-title">{line1}</text>'''
            channel_y, meta_y = 25, 46

        badge_x = w - 68
        badge_y = 298
        duration = video.get("duration", "10:00")

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <clipPath id="thumbClip_{idx}">
      <rect x="0" y="0" width="{w}" height="326" rx="14"/>
    </clipPath>
    <style>
      .yt-title {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 19px;
        fill: #FFFFFF;
      }}
      .yt-channel {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 500;
        font-size: 14.5px;
        fill: #AAAAAA;
      }}
      .yt-meta {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 400;
        font-size: 13.5px;
        fill: #AAAAAA;
      }}
      .yt-badge {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 12.5px;
        fill: #FFFFFF;
      }}
    </style>
  </defs>

  <rect width="{w}" height="{h}" fill="#0F0F0F" rx="16"/>

  <g clip-path="url(#thumbClip_{idx})">
    <image href="data:image/{mime};base64,{b64_thumb}" 
           x="0" y="0" width="{w}" height="326" 
           preserveAspectRatio="xMidYMid slice"/>
    <g transform="translate({badge_x}, {badge_y})">
      <rect x="0" y="0" width="56" height="20" rx="4" fill="#000000" fill-opacity="0.8"/>
      <text x="28" y="14" text-anchor="middle" class="yt-badge">{duration}</text>
    </g>
  </g>

  <g transform="translate(14, 342)">
    <clipPath id="avatarClip_{idx}">
      <circle cx="21" cy="21" r="21"/>
    </clipPath>
    <image href="data:image/png;base64,{b64_avatar}" 
           x="0" y="0" width="42" height="42" 
           clip-path="url(#avatarClip_{idx})"/>

    <g transform="translate(58, 14)">
      {title_svg}
      <g transform="translate(0, {channel_y})">
        <text x="0" y="0" class="yt-channel">EternoDev</text>
        <g transform="translate(72, -13) scale(0.65)" fill="#AAAAAA">
          <path d="{check_path}"/>
        </g>
      </g>
      <text x="0" y="{meta_y}" class="yt-meta">{video["views"]}</text>
    </g>

    <g transform="translate({w - 40}, 6)" fill="#AAAAAA">
      <circle cx="2" cy="2" r="2"/>
      <circle cx="2" cy="8" r="2"/>
      <circle cx="2" cy="14" r="2"/>
    </g>
  </g>
</svg>'''
        card_path = os.path.join(SVG_DIR, f"yt_card_{idx}.svg")
        with open(card_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"[OK] Tarjeta YouTube {idx} generada: {video['title']}")

# =============================================================================
# 3. ACTUALIZACIÓN AUTOMÁTICA DE README.MD
# =============================================================================
def update_readme(yt_videos, itch_games):
    readme_content = f'''<div align="center">

  <!-- CABECERA AMARILLA (#FBDA50) CON DEGRADADO RADIAL, IMAGEN ETERNODEV Y ABRIR WEB -->
  <a href="https://eternodev.com" target="_blank">
    <img src="./assets/svg/header.svg" width="100%" alt="EternoDev - Open Web">
  </a>

  <!-- SECCIÓN VÍDEOS DE YOUTUBE -->
  <h1>Vídeos de <a href="https://www.youtube.com/@eternodev" target="_blank"><img src="./assets/svg/yt_badge.svg" height="40" alt="YouTube" valign="middle"></a></h1>

  <!-- FEED YOUTUBE 2x2 (CUADRÍCULA SIN BORDES) -->
  <p align="center">
    <a href="https://www.youtube.com/watch?v={yt_videos[0]['id']}" target="_blank">
      <img src="./assets/svg/yt_card_1.svg" width="48.5%" alt="{yt_videos[0]['title']}">
    </a>
    &nbsp;
    <a href="https://www.youtube.com/watch?v={yt_videos[1]['id']}" target="_blank">
      <img src="./assets/svg/yt_card_2.svg" width="48.5%" alt="{yt_videos[1]['title']}">
    </a>
  </p>
  <p align="center">
    <a href="https://www.youtube.com/watch?v={yt_videos[2]['id']}" target="_blank">
      <img src="./assets/svg/yt_card_3.svg" width="48.5%" alt="{yt_videos[2]['title']}">
    </a>
    &nbsp;
    <a href="https://www.youtube.com/watch?v={yt_videos[3]['id']}" target="_blank">
      <img src="./assets/svg/yt_card_4.svg" width="48.5%" alt="{yt_videos[3]['title']}">
    </a>
  </p>

  <!-- SECCIÓN VIDEOJUEGOS EN ITCH.IO -->
  <p align="center">
    <a href="https://eternodev.itch.io" target="_blank">
      <img src="./assets/svg/itch_badge.svg" height="40" alt="Juegos en Itch.io" valign="middle">
    </a>
  </p>

  <!-- FEED ITCH.IO 2x3 (5 JUEGOS + TARJETA DE CATÁLOGO) -->
  <p align="center">
    <a href="{itch_games[0]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_1.svg" width="48.5%" alt="{itch_games[0]['title']}">
    </a>
    &nbsp;
    <a href="{itch_games[1]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_2.svg" width="48.5%" alt="{itch_games[1]['title']}">
    </a>
  </p>
  <p align="center">
    <a href="{itch_games[2]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_3.svg" width="48.5%" alt="{itch_games[2]['title']}">
    </a>
    &nbsp;
    <a href="{itch_games[3]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_4.svg" width="48.5%" alt="{itch_games[3]['title']}">
    </a>
  </p>
  <p align="center">
    <a href="{itch_games[4]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_5.svg" width="48.5%" alt="{itch_games[4]['title']}">
    </a>
    &nbsp;
    <a href="https://eternodev.itch.io" target="_blank">
      <img src="./assets/svg/itch_card_6.svg" width="48.5%" alt="Catálogo completo de EternoDev en Itch.io">
    </a>
  </p>

</div>
'''
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("[OK] README.md actualizado con las secciones de YouTube e Itch.io.")

def main():
    print("==================================================")
    print("  SINCRONIZACIÓN DE PERFIL: YOUTUBE & ITCH.IO     ")
    print("==================================================")
    
    itch_games = get_itch_games()
    render_itch_cards(itch_games)
    
    yt_videos = get_youtube_videos()
    render_youtube_cards(yt_videos)
    
    update_readme(yt_videos, itch_games)
    print("==================================================")
    print("  SINCRONIZACIÓN COMPLETADA CON ÉXITO             ")
    print("==================================================")

if __name__ == "__main__":
    main()
