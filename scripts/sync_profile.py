"""
=============================================================================
ETERNO DEV PROFILE - MASTER SYNC & CARD GENERATOR
Sincronización 100% dinámica de vídeos de YouTube y videojuegos de Itch.io
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

# Iconos vectoriales de plataformas oficiales de EternoDev
WIN_PATH = "M675 785 c-44 -7 -119 -18 -167 -25 l-88 -12 0 -134 0 -134 185 0 186 0 -3 157 c-3 132 -5 158 -18 159 -8 1 -51 -4 -95 -11z M220 721 l-115 -16 -3 -112 -3 -113 136 0 135 0 0 130 c0 118 -2 130 -17 129 -10 -1 -70 -9 -133 -18z M100 325 c0 -132 -14 -117 125 -135 44 -6 95 -13 113 -16 l32 -5 0 136 0 135 -135 0 -135 0 0 -115z M420 302 l0 -139 178 -24 c97 -14 180 -22 185 -19 4 4 6 76 5 161 l-3 154 -182 3 -183 2 0 -138z"
LINUX_PATH = "M350 837 c-170 -40 -225 -148 -213 -419 4 -112 3 -131 -21 -211 -14 -48 -26 -90 -26 -93 0 -3 21 -4 47 -2 l47 3 11 48 10 48 36 -31 c42 -34 79 -50 118 -50 28 0 184 70 213 97 15 13 17 12 23 -9 4 -13 14 -42 22 -65 l16 -43 97 0 98 0 -42 83 -43 82 -6 156 c-8 189 -27 264 -87 331 -22 25 -58 53 -81 62 -57 23 -152 28 -219 13z m199 -293 c19 -18 25 -36 28 -81 4 -67 -4 -85 -36 -76 -18 5 -21 10 -16 31 7 28 -10 78 -30 86 -19 7 -55 -22 -55 -45 0 -34 -44 -21 -48 14 -4 36 18 69 60 90 38 19 63 14 97 -19z m-265 -15 c28 -33 36 -89 12 -89 -7 0 -16 9 -19 20 -3 11 -13 23 -22 27 -27 10 -48 -25 -41 -69 7 -41 -6 -51 -24 -19 -23 43 -2 140 32 154 26 11 37 6 62 -24z m172 -153 c98 -44 109 -51 112 -69 5 -27 -15 -45 -100 -88 -109 -55 -139 -53 -218 12 -35 30 -60 58 -58 67 2 8 32 37 67 65 75 57 95 58 197 13z M223 315 c-20 -53 139 -84 255 -50 41 13 52 20 52 37 0 17 -4 19 -27 13 -64 -16 -199 -17 -237 -1 -32 13 -38 14 -43 1z"
MAC_PATH = "M556 829 c-58 -16 -129 -112 -112 -154 4 -11 12 -12 37 -5 61 18 114 89 107 142 -3 22 -6 24 -32 17z M265 641 c-78 -36 -115 -102 -115 -205 0 -88 31 -182 84 -253 56 -76 90 -92 149 -69 54 20 104 20 152 1 69 -29 134 18 191 137 l17 37 -41 40 c-47 46 -56 72 -50 142 4 39 12 57 38 84 29 30 32 36 19 51 -20 25 -89 54 -127 54 -18 0 -49 -7 -69 -15 -19 -8 -48 -15 -63 -15 -15 0 -44 7 -63 15 -47 19 -73 19 -122 -4z"

def fetch_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read().decode('utf-8', errors='replace'))
    except Exception as e:
        print(f"[!] Error consultando {url}: {e}")
        return None

def download_file(url, target_path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp, open(target_path, 'wb') as f:
            f.write(resp.read())
        return True
    except Exception as e:
        print(f"[!] Error descargando {url}: {e}")
        return False

def format_count(num):
    try:
        n = int(num)
        if n >= 1000000:
            return f"{n/1000000:.1f}M".replace(".0M", "M")
        if n >= 1000:
            return f"{n/1000:.1f}K".replace(".0K", "K")
        return str(n)
    except:
        return str(num)

def format_relative_date(iso_str):
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        return f"{dt.day} {meses[dt.month - 1]} {dt.year}"
    except:
        return ""

def parse_iso_duration(duration_str):
    match = re.match(r'PT(?:(\d+)M)?(?:(\d+)S)?', duration_str or "")
    if not match:
        return "10:00"
    m = match.group(1) or "0"
    s = match.group(2) or "0"
    return f"{int(m)}:{int(s):02d}"

# =============================================================================
# 1. SINCRONIZACIÓN DINÁMICA DE YOUTUBE
# =============================================================================
# Títulos y duraciones canónicas de referencia
CANONICAL_YT_DATA = {
    "wjoGjOxCTCQ": {
        "title": "¡REHICE el Juego de mis SUEÑOS! - DevBlog 2",
        "duration": "10:42",
        "date": "3 sept 2026"
    },
    "DFR5UtAuHTw": {
        "title": "Sobreviví a mi PRIMERA GameJam",
        "duration": "9:26",
        "date": "11 oct 2025"
    },
    "bRbhRWQvqs8": {
        "title": "Hice un VTUBER en 48 HORAS",
        "duration": "8:33",
        "date": "20 abr 2025"
    },
    "F1-R5hIjGLM": {
        "title": "¡Creando Mi Propio JUEGO Desde CERO! - DevBlog 1",
        "duration": "9:02",
        "date": "22 nov 2024"
    }
}

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

def fetch_youtube_videos():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    channel_id = "UCewJv1M1YAKfLcbld6iWxWg"
    videos = []

    # 1. Si la API Key está configurada, consultar YouTube Data API v3
    if api_key:
        print("[+] Conectando a YouTube Data API v3 oficial...")
        chan_data = fetch_json(f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}")
        uploads_id = chan_data.get("items", [{}])[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads") if chan_data else None
        if uploads_id:
            items_data = fetch_json(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_id}&maxResults=8&key={api_key}")
            if items_data and "items" in items_data:
                vids_ids = [i["snippet"]["resourceId"]["videoId"] for i in items_data["items"] if "snippet" in i]
                if vids_ids:
                    stats_data = fetch_json(f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={','.join(vids_ids)}&key={api_key}")
                    if stats_data and "items" in stats_data:
                        for item in stats_data["items"]:
                            v_id = item["id"]
                            s = item["snippet"]
                            canon = CANONICAL_YT_DATA.get(v_id, {})
                            title = canon.get("title") or s.get("title", "")
                            dur = canon.get("duration") or parse_iso_duration(item.get("contentDetails", {}).get("duration"))
                            views_raw = item.get("statistics", {}).get("viewCount", "0")
                            views_str = f"{format_count(views_raw)} visualizaciones"
                            date_str = canon.get("date") or format_relative_date(s.get("publishedAt"))
                            meta_str = f"{views_str} • {date_str}" if date_str else views_str
                            
                            cover_url = s.get("thumbnails", {}).get("maxres", {}).get("url") or f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
                            t_file = f"thumb_{v_id}.jpg"
                            t_path = os.path.join(THUMB_DIR, t_file)
                            if not os.path.exists(t_path):
                                download_file(cover_url, t_path)

                            videos.append({
                                "id": v_id,
                                "title": title,
                                "file": t_file if os.path.exists(t_path) else "thumb_rehice.png",
                                "duration": dur,
                                "views": meta_str
                            })

    # 2. Si no hay API Key, consultar fuente en vivo de EternoDev-Official
    if not videos:
        print("[*] Leyendo datos en vivo desde videos.json de EternoDev-Official...")
        live_vids = fetch_json("https://raw.githubusercontent.com/paucg06/EternoDev-Official/main/videos.json")
        if live_vids:
            for v in live_vids:
                v_id = v["id"]
                canon = CANONICAL_YT_DATA.get(v_id, {})
                title = canon.get("title") or v.get("title", "")
                dur = canon.get("duration") or "10:00"
                views_val = v.get("views") or format_count(v.get("raw_views", 0))
                date_str = canon.get("date") or format_relative_date(v.get("published_at"))
                meta_str = f"{views_val} visualizaciones • {date_str}" if date_str else f"{views_val} visualizaciones"
                
                t_file = f"thumb_{v_id}.jpg"
                t_path = os.path.join(THUMB_DIR, t_file)
                if not os.path.exists(t_path) and v.get("cover_url"):
                    download_file(v["cover_url"], t_path)

                videos.append({
                    "id": v_id,
                    "title": title,
                    "file": t_file if os.path.exists(t_path) else "thumb_rehice.png",
                    "duration": dur,
                    "views": meta_str
                })

    return videos

def render_youtube_cards(videos):
    logo_path = os.path.join(THUMB_DIR, "logo.png")
    b64_avatar = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64_avatar = base64.b64encode(f.read()).decode("utf-8")

    w, h = 580, 445
    check_path = "M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.4-1.4 3.6 3.6 7.6-7.6L19 8l-9 9z"

    for idx, video in enumerate(videos[:4], start=1):
        thumb_path = os.path.join(THUMB_DIR, video.get("file", "thumb_rehice.png"))
        if not os.path.exists(thumb_path):
            thumb_path = os.path.join(THUMB_DIR, "thumb_rehice.png")

        with open(thumb_path, "rb") as f:
            b64_thumb = base64.b64encode(f.read()).decode("utf-8")

        mime = "png" if thumb_path.endswith(".png") else "jpeg"
        line1, line2 = wrap_youtube_title(video["title"], max_chars=35)
        if line2:
            title_svg = f'''<text x="0" y="0" class="yt-title">{line1}</text>
      <text x="0" y="24" class="yt-title">{line2}</text>'''
            channel_y, meta_y = 48, 68
        else:
            title_svg = f'''<text x="0" y="0" class="yt-title">{line1}</text>'''
            channel_y, meta_y = 25, 46

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
    <g transform="translate({w - 68}, 298)">
      <rect x="0" y="0" width="56" height="20" rx="4" fill="#000000" fill-opacity="0.8"/>
      <text x="28" y="14" text-anchor="middle" class="yt-badge">{video["duration"]}</text>
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
        print(f"[OK] Tarjeta YouTube {idx} generada con {video['views']}: {video['title']}")

# =============================================================================
# 2. SINCRONIZACIÓN DINÁMICA DE ITCH.IO
# =============================================================================
KNOWN_DESCRIPTIONS = {
    "castlecat-rpg": {
        "genre": "Adventure",
        "desc_lines": ["¡Naciste gato, pero morirás como leyenda!"]
    },
    "oonga-bunga": {
        "genre": "Fighting",
        "desc_lines": [
            "Compite con tus amigos para convertirte",
            "en el líder de la tribu. ¡Solo habrá un ganador!"
        ]
    },
    "soap-dodger": {
        "genre": "Action",
        "desc_lines": [
            "Agudiza tus reflejos en este peliagudo",
            "Bullet Hell. ¡No pierdas bocanadas de aire!"
        ]
    },
    "space-blitz": {
        "genre": "Shooter",
        "desc_lines": [
            "Combate espacial de ritmo rápido. Destruye",
            "enemigos y sobrevive a oleadas en el espacio."
        ]
    },
    "verdades-incompletas": {
        "genre": "Visual Novel",
        "desc_lines": [
            "Estás muerto... Descubre quién te asesinó",
            "mientras tus tres amigos investigan tu hogar."
        ]
    }
}

def render_platform_bar(has_browser, has_win, has_lin, has_mac):
    elements = []
    x_cur = 0
    if has_browser:
        elements.append(f'''<g transform="translate({x_cur}, 0)">
          <rect width="102" height="20" rx="3" fill="#EEEEEE"/>
          <text x="51" y="14" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="10.8" fill="#111111">Play in browser</text>
        </g>''')
        x_cur += 112
        
    icon_scale = "scale(0.020, -0.020)"
    y_baseline = 17.5
    
    if has_win:
        elements.append(f'''<g transform="translate({x_cur}, {y_baseline}) {icon_scale}" fill="#FFFFFF">
          <path d="{WIN_PATH}"/>
        </g>''')
        x_cur += 24
        
    if has_lin:
        elements.append(f'''<g transform="translate({x_cur}, {y_baseline}) {icon_scale}" fill="#FFFFFF">
          <path d="{LINUX_PATH}"/>
        </g>''')
        x_cur += 24
        
    if has_mac:
        elements.append(f'''<g transform="translate({x_cur}, {y_baseline}) {icon_scale}" fill="#FFFFFF">
          <path d="{MAC_PATH}"/>
        </g>''')
        x_cur += 24
        
    return "".join(elements)

def generate_itch_card(game, index):
    w, h = 380, 445
    cover_h = 302 # Exact 315x250 aspect ratio
    
    thumb_path = os.path.join(ITCH_THUMB_DIR, game["file"])
    with open(thumb_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")
        
    platforms_svg = render_platform_bar(game.get("browser", False), game.get("win", False), game.get("linux", False), game.get("mac", False))
    
    desc_svg = []
    y_desc = 352
    for line in game.get("desc_lines", []):
        desc_svg.append(f'<text x="14" y="{y_desc}" class="game-desc">{line}</text>')
        y_desc += 17
    desc_str = "\n  ".join(desc_svg)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <clipPath id="itchClip_{index}">
      <rect x="0" y="0" width="{w}" height="{cover_h}" rx="3"/>
    </clipPath>
    <style>
      .game-title {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 19px;
        fill: #FFFFFF;
      }}
      .game-desc {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 400;
        font-size: 12.5px;
        fill: #FFFFFF;
      }}
      .game-genre {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 13px;
        fill: #AAAAAA;
      }}
    </style>
  </defs>

  <rect width="{w}" height="{h}" fill="#0F0F0F" rx="4"/>

  <g clip-path="url(#itchClip_{index})">
    <image href="data:image/png;base64,{b64_img}" 
           x="0" y="0" width="{w}" height="{cover_h}" 
           preserveAspectRatio="none"/>
  </g>

  <text x="14" y="330" class="game-title">{game["title"]}</text>
  
  {desc_str}
  
  <text x="14" y="394" class="game-genre">{game["genre"]}</text>

  <g transform="translate(14, 408)">
    {platforms_svg}
  </g>
</svg>'''
    return svg

def fetch_itch_games():
    api_key = os.environ.get("ITCH_API_KEY")
    games = []
    
    # 1. Si la API Key de Itch.io está configurada, consultar oficial
    if api_key:
        print("[+] Conectando a Itch.io API oficial...")
        data = fetch_json("https://api.itch.io/profile/games", headers={'Authorization': f'Bearer {api_key}'})
        if data and "games" in data:
            for g in data["games"]:
                if g.get("published") is not False:
                    slug = (g.get("url") or "").rstrip("/").split("/")[-1]
                    file_name = f"{slug.replace('-', '_')}.png"
                    t_path = os.path.join(ITCH_THUMB_DIR, file_name)
                    if not os.path.exists(t_path) and g.get("cover_url"):
                        download_file(g["cover_url"], t_path)
                        
                    meta = KNOWN_DESCRIPTIONS.get(slug, {})
                    genre = meta.get("genre") or "Videojuego"
                    desc_lines = meta.get("desc_lines") or [g.get("short_text", "")[:45]]
                    
                    games.append({
                        "id": g.get("id"),
                        "title": g.get("title"),
                        "url": g.get("url"),
                        "file": file_name,
                        "genre": genre,
                        "desc_lines": desc_lines,
                        "browser": g.get("type") == "html",
                        "win": bool(g.get("p_windows")),
                        "linux": bool(g.get("p_linux")),
                        "mac": bool(g.get("p_osx"))
                    })

    # 2. Si no hay API Key, consultar fuente en vivo de EternoDev-Official
    if not games:
        print("[*] Leyendo datos en vivo desde games.json de EternoDev-Official...")
        live_games = fetch_json("https://raw.githubusercontent.com/paucg06/EternoDev-Official/main/games.json")
        if live_games:
            for g in live_games:
                slug = (g.get("url") or "").rstrip("/").split("/")[-1]
                file_name = f"{slug.replace('-', '_')}.png"
                t_path = os.path.join(ITCH_THUMB_DIR, file_name)
                if not os.path.exists(t_path) and g.get("cover_url"):
                    download_file(g["cover_url"], t_path)
                    
                meta = KNOWN_DESCRIPTIONS.get(slug, {})
                genre = g.get("genre") or meta.get("genre") or "Videojuego"
                desc_lines = meta.get("desc_lines") or [g.get("short_text", "")[:45]]

                games.append({
                    "id": g.get("id"),
                    "title": g.get("title"),
                    "url": g.get("url"),
                    "file": file_name,
                    "genre": genre,
                    "desc_lines": desc_lines,
                    "browser": bool(g.get("p_browser")) or g.get("type") == "html",
                    "win": bool(g.get("p_windows")),
                    "linux": bool(g.get("p_linux")),
                    "mac": bool(g.get("p_osx"))
                })

    for idx, game in enumerate(games, start=1):
        svg_code = generate_itch_card(game, idx)
        out_path = os.path.join(SVG_DIR, f"itch_card_{idx}.svg")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_code)
        print(f"[OK] Tarjeta Itch.io {idx} generada: {game['title']}")

    return games

# =============================================================================
# 3. CONSTRUCCIÓN AUTOMÁTICA DEL README.MD
# =============================================================================
def build_readme(yt_videos, itch_games):
    # Generar HTML para filas de YouTube (2 por fila)
    yt_rows = []
    for i in range(0, min(len(yt_videos), 4), 2):
        v1 = yt_videos[i]
        card1 = f'<a href="https://www.youtube.com/watch?v={v1["id"]}" target="_blank"><img src="./assets/svg/yt_card_{i+1}.svg" width="48.5%" alt="{v1["title"]}"></a>'
        if i + 1 < len(yt_videos):
            v2 = yt_videos[i+1]
            card2 = f'<a href="https://www.youtube.com/watch?v={v2["id"]}" target="_blank"><img src="./assets/svg/yt_card_{i+2}.svg" width="48.5%" alt="{v2["title"]}"></a>'
            yt_rows.append(f'  <p align="center">\n    {card1}\n    &nbsp;\n    {card2}\n  </p>')
        else:
            yt_rows.append(f'  <p align="center">\n    {card1}\n  </p>')
    yt_html = "\n".join(yt_rows)

    # Generar HTML para filas de Itch.io (3 por fila, sólo los juegos existentes)
    itch_rows = []
    for i in range(0, len(itch_games), 3):
        chunk = itch_games[i:i+3]
        links = []
        for j, g in enumerate(chunk):
            idx = i + j + 1
            links.append(f'<a href="{g["url"]}" target="_blank"><img src="./assets/svg/itch_card_{idx}.svg" width="32%" alt="{g["title"]}"></a>')
        row_str = "\n    &nbsp;\n    ".join(links)
        itch_rows.append(f'  <p align="center">\n    {row_str}\n  </p>')
    itch_html = "\n".join(itch_rows)

    readme_content = f'''<div align="center">

  <!-- CABECERA AMARILLA (#FBDA50) CON DEGRADADO RADIAL, IMAGEN ETERNODEV Y ABRIR WEB -->
  <a href="https://eternodev.com" target="_blank">
    <img src="./assets/svg/header.svg" width="100%" alt="EternoDev - Open Web">
  </a>

  <!-- SECCIÓN VÍDEOS DE YOUTUBE -->
  <h1>Vídeos de <a href="https://www.youtube.com/@eternodev" target="_blank"><img src="./assets/svg/yt_badge.svg" height="40" alt="YouTube" valign="middle"></a></h1>

  <!-- FEED YOUTUBE 2x2 (CUADRÍCULA SIN BORDES) -->
{yt_html}

  <br>
  <br>

  <!-- SECCIÓN JUEGOS EN ITCH.IO -->
  <h1>Juegos en <a href="https://eternodev.itch.io" target="_blank"><img src="./assets/svg/itch_badge.svg" height="40" alt="Itch.io" valign="middle"></a></h1>

  <!-- FEED ITCH.IO (SOLO JUEGOS PUBLICADOS) -->
{itch_html}

</div>
'''
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("[OK] README.md actualizado dinámicamente con las dos secciones.")

def main():
    print("==================================================")
    print("  SINCRONIZACIÓN DE PERFIL: YOUTUBE & ITCH.IO     ")
    print("==================================================")
    yt_videos = fetch_youtube_videos()
    render_youtube_cards(yt_videos)
    
    itch_games = fetch_itch_games()
    
    build_readme(yt_videos, itch_games)
    print("==================================================")
    print("  SINCRONIZACIÓN COMPLETADA CON ÉXITO             ")
    print("==================================================")

if __name__ == "__main__":
    main()
