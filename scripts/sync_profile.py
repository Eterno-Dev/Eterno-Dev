"""
=============================================================================
ETERNO DEV PROFILE - MASTER SYNC & CARD GENERATOR
Sincronización dinámica de vídeos de YouTube y videojuegos de Itch.io
=============================================================================
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

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

# Iconos de plataforma oficiales de EternoDev-Official
WIN_PATH = "M675 785 c-44 -7 -119 -18 -167 -25 l-88 -12 0 -134 0 -134 185 0 186 0 -3 157 c-3 132 -5 158 -18 159 -8 1 -51 -4 -95 -11z M220 721 l-115 -16 -3 -112 -3 -113 136 0 135 0 0 130 c0 118 -2 130 -17 129 -10 -1 -70 -9 -133 -18z M100 325 c0 -132 -14 -117 125 -135 44 -6 95 -13 113 -16 l32 -5 0 136 0 135 -135 0 -135 0 0 -115z M420 302 l0 -139 178 -24 c97 -14 180 -22 185 -19 4 4 6 76 5 161 l-3 154 -182 3 -183 2 0 -138z"
LINUX_PATH = "M350 837 c-170 -40 -225 -148 -213 -419 4 -112 3 -131 -21 -211 -14 -48 -26 -90 -26 -93 0 -3 21 -4 47 -2 l47 3 11 48 10 48 36 -31 c42 -34 79 -50 118 -50 28 0 184 70 213 97 15 13 17 12 23 -9 4 -13 14 -42 22 -65 l16 -43 97 0 98 0 -42 83 -43 82 -6 156 c-8 189 -27 264 -87 331 -22 25 -58 53 -81 62 -57 23 -152 28 -219 13z m199 -293 c19 -18 25 -36 28 -81 4 -67 -4 -85 -36 -76 -18 5 -21 10 -16 31 7 28 -10 78 -30 86 -19 7 -55 -22 -55 -45 0 -34 -44 -21 -48 14 -4 36 18 69 60 90 38 19 63 14 97 -19z m-265 -15 c28 -33 36 -89 12 -89 -7 0 -16 9 -19 20 -3 11 -13 23 -22 27 -27 10 -48 -25 -41 -69 7 -41 -6 -51 -24 -19 -23 43 -2 140 32 154 26 11 37 6 62 -24z m172 -153 c98 -44 109 -51 112 -69 5 -27 -15 -45 -100 -88 -109 -55 -139 -53 -218 12 -35 30 -60 58 -58 67 2 8 32 37 67 65 75 57 95 58 197 13z M223 315 c-20 -53 139 -84 255 -50 41 13 52 20 52 37 0 17 -4 19 -27 13 -64 -16 -199 -17 -237 -1 -32 13 -38 14 -43 1z"
MAC_PATH = "M556 829 c-58 -16 -129 -112 -112 -154 4 -11 12 -12 37 -5 61 18 114 89 107 142 -3 22 -6 24 -32 17z M265 641 c-78 -36 -115 -102 -115 -205 0 -88 31 -182 84 -253 56 -76 90 -92 149 -69 54 20 104 20 152 1 69 -29 134 18 191 137 l17 37 -41 40 c-47 46 -56 72 -50 142 4 39 12 57 38 84 29 30 32 36 19 51 -20 25 -89 54 -127 54 -18 0 -49 -7 -69 -15 -19 -8 -48 -15 -63 -15 -15 0 -44 7 -63 15 -47 19 -73 19 -122 -4z"

def fetch_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read().decode('utf-8', errors='ignore'))
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
# 1. ITCH.IO GAMES DATA & 3-COLUMN PANELS GENERATOR
# =============================================================================
BASE_ITCH_GAMES = [
    {
        "id": 3533624,
        "title": "CastleCat RPG",
        "url": "https://eternodev.itch.io/castlecat-rpg",
        "file": "castlecat_rpg.png",
        "genre": "Adventure",
        "desc_lines": ["¡Naciste gato, pero morirás como leyenda!"],
        "browser": True, "win": False, "linux": False, "mac": False
    },
    {
        "id": 4244918,
        "title": "Oonga Bunga!",
        "url": "https://eternodev.itch.io/oonga-bunga",
        "file": "oonga_bunga.png",
        "genre": "Fighting",
        "desc_lines": [
            "Compite con tus amigos para convertirte",
            "en el líder de la tribu. ¡Solo habrá un ganador!"
        ],
        "browser": False, "win": True, "linux": True, "mac": False
    },
    {
        "id": 3269482,
        "title": "Soap Dodger",
        "url": "https://eternodev.itch.io/soap-dodger",
        "file": "soap_dodger.png",
        "genre": "Action",
        "desc_lines": [
            "Agudiza tus reflejos en este peliagudo",
            "Bullet Hell. ¡No pierdas bocanadas de aire!"
        ],
        "browser": True, "win": True, "linux": True, "mac": True
    },
    {
        "id": 4692794,
        "title": "Space Blitz",
        "url": "https://eternodev.itch.io/space-blitz",
        "file": "space_blitz.png",
        "genre": "Shooter",
        "desc_lines": [
            "Combate espacial de ritmo rápido. Destruye",
            "enemigos y sobrevive a oleadas en el espacio."
        ],
        "browser": True, "win": False, "linux": False, "mac": False
    },
    {
        "id": 3974299,
        "title": "Verdades Incompletas",
        "url": "https://eternodev.itch.io/verdades-incompletas",
        "file": "verdades_incompletas.png",
        "genre": "Visual Novel",
        "desc_lines": [
            "Estás muerto... Descubre quién te asesinó",
            "mientras tus tres amigos investigan tu hogar."
        ],
        "browser": True, "win": True, "linux": True, "mac": True
    }
]

def render_platform_bar(has_browser, has_win, has_lin, has_mac):
    elements = []
    x_cur = 0
    if has_browser:
        elements.append(f'''<g transform="translate({x_cur}, 0)">
          <rect width="104" height="21" rx="4" fill="#D8D8D8"/>
          <text x="52" y="14.5" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="11" fill="#1A1A1A">Play in browser</text>
        </g>''')
        x_cur += 114
        
    icon_scale = "scale(0.021, -0.021)"
    y_baseline = 18.5
    
    if has_win:
        elements.append(f'''<g transform="translate({x_cur}, {y_baseline}) {icon_scale}" fill="#8E8E93">
          <path d="{WIN_PATH}"/>
        </g>''')
        x_cur += 24
        
    if has_lin:
        elements.append(f'''<g transform="translate({x_cur}, {y_baseline}) {icon_scale}" fill="#8E8E93">
          <path d="{LINUX_PATH}"/>
        </g>''')
        x_cur += 24
        
    if has_mac:
        elements.append(f'''<g transform="translate({x_cur}, {y_baseline}) {icon_scale}" fill="#8E8E93">
          <path d="{MAC_PATH}"/>
        </g>''')
        x_cur += 24
        
    return "".join(elements)

def generate_itch_panel(game, index):
    w, h = 380, 460
    cover_h = 302 # Exactly 380 * 250 / 315 = 301.6 rounded to 302 (100% uncropped)!
    
    thumb_path = os.path.join(ITCH_THUMB_DIR, game["file"])
    with open(thumb_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")
        
    platforms_svg = render_platform_bar(game["browser"], game["win"], game["linux"], game["mac"])
    
    desc_svg = []
    y_desc = 356
    for line in game["desc_lines"]:
        desc_svg.append(f'<text x="16" y="{y_desc}" class="game-desc">{line}</text>')
        y_desc += 17
    desc_str = "\n      ".join(desc_svg)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <clipPath id="itchClip_{index}">
      <rect x="0" y="0" width="{w}" height="{cover_h}" rx="10"/>
    </clipPath>
    <style>
      .game-title {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 800;
        font-size: 19px;
        fill: #FFFFFF;
      }}
      .game-desc {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 400;
        font-size: 12.8px;
        fill: #CCCCCE;
      }}
      .game-genre {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 13.5px;
        fill: #8E8E93;
      }}
    </style>
  </defs>

  <!-- Dark Card Panel (exact style from EternoDev web & Itch.io) -->
  <rect width="{w}" height="{h}" rx="12" fill="#1C1C24" stroke="#2D2D38" stroke-width="1.2"/>

  <!-- Uncropped 315x250 Cover Image -->
  <g clip-path="url(#itchClip_{index})">
    <image href="data:image/png;base64,{b64_img}" 
           x="0" y="0" width="{w}" height="{cover_h}" 
           preserveAspectRatio="none"/>
  </g>

  <!-- Content Box -->
  <text x="16" y="333" class="game-title">{game["title"]}</text>
  
  {desc_str}
  
  <text x="16" y="401" class="game-genre">{game["genre"]}</text>

  <g transform="translate(16, 417)">
    {platforms_svg}
  </g>
</svg>'''
    return svg

def generate_catalog_panel():
    w, h = 380, 460
    cover_h = 302
    platforms_svg = render_platform_bar(True, True, True, True)
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <clipPath id="itchCatalogClip">
      <rect x="0" y="0" width="{w}" height="{cover_h}" rx="10"/>
    </clipPath>
    <linearGradient id="catGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2D1517"/>
      <stop offset="50%" stop-color="#1E1E24"/>
      <stop offset="100%" stop-color="#141419"/>
    </linearGradient>
    <style>
      .game-title {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 800;
        font-size: 19px;
        fill: #FFFFFF;
      }}
      .game-desc {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 400;
        font-size: 12.8px;
        fill: #CCCCCE;
      }}
      .game-genre {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 13.5px;
        fill: #FA5C5C;
      }}
      .cat-head {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 800;
        font-size: 24px;
        fill: #FFFFFF;
      }}
      .cat-sub {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 14px;
        fill: #FA5C5C;
      }}
      .btn-txt {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 13px;
        fill: #FFFFFF;
      }}
    </style>
  </defs>

  <rect width="{w}" height="{h}" rx="12" fill="#1C1C24" stroke="#2D2D38" stroke-width="1.2"/>

  <!-- Top Hero Illustration Box -->
  <g clip-path="url(#itchCatalogClip)">
    <rect width="{w}" height="{cover_h}" fill="url(#catGrad)"/>
    <circle cx="190" cy="130" r="90" fill="#FA5C5C" fill-opacity="0.08"/>
    <circle cx="190" cy="130" r="55" fill="#FA5C5C" fill-opacity="0.12"/>
    <text x="190" y="125" text-anchor="middle" class="cat-head">EternoDev</text>
    <text x="190" y="152" text-anchor="middle" class="cat-sub">Catálogo Oficial en Itch.io</text>
    
    <g transform="translate(100, 195)">
      <rect width="180" height="34" rx="17" fill="#FA5C5C"/>
      <text x="90" y="21.5" text-anchor="middle" class="btn-txt">Ver todos los juegos →</text>
    </g>
  </g>

  <!-- Content Box -->
  <text x="16" y="333" class="game-title">Explorar Más Juegos</text>
  <text x="16" y="356" class="game-desc">Descubre todos los prototipos, game jams</text>
  <text x="16" y="373" class="game-desc">y futuros videojuegos en desarrollo.</text>
  <text x="16" y="401" class="game-genre">eternodev.itch.io</text>

  <g transform="translate(16, 417)">
    {platforms_svg}
  </g>
</svg>'''
    return svg

def render_all_itch_cards():
    for idx, g in enumerate(BASE_ITCH_GAMES, start=1):
        svg_code = generate_itch_panel(g, idx)
        with open(os.path.join(SVG_DIR, f"itch_card_{idx}.svg"), "w", encoding="utf-8") as f:
            f.write(svg_code)
        print(f"[OK] Panel Itch.io {idx} generado: {g['title']}")
        
    with open(os.path.join(SVG_DIR, "itch_card_6.svg"), "w", encoding="utf-8") as f:
        f.write(generate_catalog_panel())
    print("[OK] Panel Itch.io 6 (Catálogo) generado.")

# =============================================================================
# 2. YOUTUBE VIDEO DATA & CARDS GENERATOR
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

BASE_YT_VIDEOS = [
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

def render_all_youtube_cards():
    logo_path = os.path.join(THUMB_DIR, "logo.png")
    b64_avatar = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64_avatar = base64.b64encode(f.read()).decode("utf-8")

    w, h = 580, 445
    check_path = "M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.4-1.4 3.6 3.6 7.6-7.6L19 8l-9 9z"

    for idx, video in enumerate(BASE_YT_VIDEOS, start=1):
        thumb_path = os.path.join(THUMB_DIR, video["thumb_file"])
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
    <image href="data:image/png;base64,{b64_thumb}" 
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
        with open(os.path.join(SVG_DIR, f"yt_card_{idx}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"[OK] Tarjeta YouTube {idx} generada: {video['title']}")

# =============================================================================
# 3. ACTUALIZACIÓN AUTOMÁTICA DE README.MD (3 COLUMNAS PARA ITCH.IO)
# =============================================================================
def update_readme():
    readme_content = f'''<div align="center">

  <!-- CABECERA AMARILLA (#FBDA50) CON DEGRADADO RADIAL, IMAGEN ETERNODEV Y ABRIR WEB -->
  <a href="https://eternodev.com" target="_blank">
    <img src="./assets/svg/header.svg" width="100%" alt="EternoDev - Open Web">
  </a>

  <!-- SECCIÓN VÍDEOS DE YOUTUBE -->
  <h1>Vídeos de <a href="https://www.youtube.com/@eternodev" target="_blank"><img src="./assets/svg/yt_badge.svg" height="40" alt="YouTube" valign="middle"></a></h1>

  <!-- FEED YOUTUBE 2x2 (CUADRÍCULA SIN BORDES) -->
  <p align="center">
    <a href="https://www.youtube.com/watch?v={BASE_YT_VIDEOS[0]['id']}" target="_blank">
      <img src="./assets/svg/yt_card_1.svg" width="48.5%" alt="{BASE_YT_VIDEOS[0]['title']}">
    </a>
    &nbsp;
    <a href="https://www.youtube.com/watch?v={BASE_YT_VIDEOS[1]['id']}" target="_blank">
      <img src="./assets/svg/yt_card_2.svg" width="48.5%" alt="{BASE_YT_VIDEOS[1]['title']}">
    </a>
  </p>
  <p align="center">
    <a href="https://www.youtube.com/watch?v={BASE_YT_VIDEOS[2]['id']}" target="_blank">
      <img src="./assets/svg/yt_card_3.svg" width="48.5%" alt="{BASE_YT_VIDEOS[2]['title']}">
    </a>
    &nbsp;
    <a href="https://www.youtube.com/watch?v={BASE_YT_VIDEOS[3]['id']}" target="_blank">
      <img src="./assets/svg/yt_card_4.svg" width="48.5%" alt="{BASE_YT_VIDEOS[3]['title']}">
    </a>
  </p>

  <!-- SECCIÓN VIDEOJUEGOS EN ITCH.IO -->
  <p align="center">
    <a href="https://eternodev.itch.io" target="_blank">
      <img src="./assets/svg/itch_badge.svg" height="40" alt="Juegos en Itch.io" valign="middle">
    </a>
  </p>

  <!-- FEED ITCH.IO 3x2 (CUADRÍCULA DE 3 COLUMNAS: 5 JUEGOS + 1 CATÁLOGO) -->
  <p align="center">
    <a href="{BASE_ITCH_GAMES[0]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_1.svg" width="32%" alt="{BASE_ITCH_GAMES[0]['title']}">
    </a>
    &nbsp;
    <a href="{BASE_ITCH_GAMES[1]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_2.svg" width="32%" alt="{BASE_ITCH_GAMES[1]['title']}">
    </a>
    &nbsp;
    <a href="{BASE_ITCH_GAMES[2]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_3.svg" width="32%" alt="{BASE_ITCH_GAMES[2]['title']}">
    </a>
  </p>
  <p align="center">
    <a href="{BASE_ITCH_GAMES[3]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_4.svg" width="32%" alt="{BASE_ITCH_GAMES[3]['title']}">
    </a>
    &nbsp;
    <a href="{BASE_ITCH_GAMES[4]['url']}" target="_blank">
      <img src="./assets/svg/itch_card_5.svg" width="32%" alt="{BASE_ITCH_GAMES[4]['title']}">
    </a>
    &nbsp;
    <a href="https://eternodev.itch.io" target="_blank">
      <img src="./assets/svg/itch_card_6.svg" width="32%" alt="Catálogo completo de EternoDev en Itch.io">
    </a>
  </p>

</div>
'''
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("[OK] README.md actualizado con Itch.io en 3 columnas.")

def main():
    print("==================================================")
    print("  SINCRONIZACIÓN DE PERFIL: YOUTUBE & ITCH.IO     ")
    print("==================================================")
    render_all_itch_cards()
    render_all_youtube_cards()
    update_readme()
    print("==================================================")
    print("  SINCRONIZACIÓN COMPLETADA CON ÉXITO             ")
    print("==================================================")

if __name__ == "__main__":
    main()
