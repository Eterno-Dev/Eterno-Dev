"""
=============================================================================
GENERADOR Y ACTUALIZADOR AUTOMÁTICO DE TARJETAS DE YOUTUBE PARA ETERNODEV
=============================================================================
Características:
1. Formato exacto de YouTube con soporte inteligente para títulos de 1 o 2 líneas.
   - Altura estándar constante (viewBox 0 0 580 445) para que todas las tarjetas
     tengan exactamente las mismas dimensiones y encajen a la perfección.
   - Si un título es largo (ej. "¡Creando Mi Propio ROGUELIKE Desde CERO!- DevBlog 1"),
     se divide limpiamente en 2 líneas sin desbordarse ni cortarse.
   - Si excediese 2 líneas, añade puntos suspensivos (...) tal como hace YouTube nativo.
2. Actualización automática de estadísticas de visualizaciones y fecha en tiempo real.
3. Lee miniaturas desde assets/thumbnail/ y exporta las tarjetas a assets/svg/.
=============================================================================
"""

import os
import urllib.request
import base64
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
THUMB_DIR = os.path.join(ASSETS_DIR, "thumbnail")
SVG_DIR = os.path.join(ASSETS_DIR, "svg")

os.makedirs(SVG_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

CHANNEL_NAME = "EternoDev"
AVATAR_PATH = os.path.join(THUMB_DIR, "logo.png")

# Lista de vídeos a mostrar en el feed
VIDEOS = [
    {
        "id": "wjoGjOxCTCQ",
        "title": "¡REHICE el Juego de mis SUEÑOS! - DevBlog 2",
        "duration": "10:42",
        "views": "1,3 K visualizaciones • hace 1 mes",
        "url": "https://www.youtube.com/watch?v=wjoGjOxCTCQ",
        "thumbnail_file": "thumb_rehice.png"
    },
    {
        "id": "DFR5UtAuHTw",
        "title": "Sobreviví a mi PRIMERA GameJam",
        "duration": "9:26",
        "views": "191 visualizaciones • hace 2 meses",
        "url": "https://www.youtube.com/watch?v=DFR5UtAuHTw",
        "thumbnail_file": "thumb_gamejam.png"
    },
    {
        "id": "bRbhRWQvqs8",
        "title": "Hice un VTUBER en 48 HORAS",
        "duration": "8:33",
        "views": "167 visualizaciones • hace 2 meses",
        "url": "https://www.youtube.com/watch?v=bRbhRWQvqs8",
        "thumbnail_file": "thumb_vtuber.png"
    },
    {
        "id": "F1-R5hIjGLM",
        "title": "¡Creando Mi Propio ROGUELIKE Desde CERO!- DevBlog 1",
        "duration": "9:02",
        "views": "1,1 K visualizaciones • hace 3 meses",
        "url": "https://www.youtube.com/watch?v=F1-R5hIjGLM",
        "thumbnail_file": "thumb_roguelike.png"
    }
]

def wrap_youtube_title(title, max_chars=34):
    """
    Divide un título en un máximo de 2 líneas con límite de caracteres.
    Si supera las 2 líneas, trunca con puntos suspensivos (...) como YouTube nativo.
    """
    words = title.split()
    line1 = []
    line2 = []
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
                # Excede la 2da línea -> truncar con '...'
                line2_str = " ".join(line2)
                if len(line2_str) + len(w) + 1 > max_chars:
                    if not line2_str.endswith("..."):
                        if len(line2_str) <= max_chars - 3:
                            line2.append("...")
                        else:
                            line2[-1] = line2[-1][:max(1, max_chars - 4)] + "..."
                break

    l1 = " ".join(line1)
    l2 = " ".join(line2)
    return l1, l2

def update_video_stats(video):
    vid_id = video["id"]
    try:
        url = f"https://www.youtube.com/watch?v={vid_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
        
        sv = re.findall(r'"shortViewCount":\{"simpleText":"([^"]+)"', html)
        views_str = sv[0] if sv else None
        
        dt = re.findall(r'"dateText":\{"simpleText":"([^"]+)"', html)
        date_str = dt[0] if dt else None
        
        if views_str and date_str:
            video["views"] = f"{views_str} • {date_str}"
            print(f"  [+] En vivo: {vid_id} -> {video['views']}")
        elif views_str:
            old_parts = video["views"].split("•")
            time_part = old_parts[1].strip() if len(old_parts) > 1 else ""
            video["views"] = f"{views_str} • {time_part}"
            print(f"  [+] En vivo: {vid_id} -> {video['views']}")
    except Exception as e:
        print(f"  [-] Manteniendo datos para {vid_id} ({e})")

def get_base64_avatar():
    if os.path.exists(AVATAR_PATH):
        with open(AVATAR_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def get_base64_thumbnail(video):
    local_file = video.get("thumbnail_file")
    if local_file:
        full_local = os.path.join(THUMB_DIR, local_file)
        if os.path.exists(full_local):
            with open(full_local, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8"), "png" if full_local.endswith(".png") else "jpeg"
    
    vid_id = video["id"]
    cache_file = os.path.join(THUMB_DIR, f"thumb_{vid_id}.jpg")
    if not os.path.exists(cache_file):
        for quality in ["maxresdefault.jpg", "hqdefault.jpg"]:
            try:
                thumb_url = f"https://i.ytimg.com/vi/{vid_id}/{quality}"
                req = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as resp:
                    data = resp.read()
                    with open(cache_file, 'wb') as f:
                        f.write(data)
                break
            except Exception:
                continue
    
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8"), "jpeg"
    return "", "jpeg"

def generate_card(video, index, b64_avatar):
    # Dimensiones uniformes para todas las tarjetas (580 x 445)
    w, h = 580, 445
    b64_thumb, mime_type = get_base64_thumbnail(video)
    check_path = "M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.4-1.4 3.6 3.6 7.6-7.6L19 8l-9 9z"

    badge_x = w - 68
    badge_y = 298

    # Procesar líneas de título
    line1, line2 = wrap_youtube_title(video["title"], max_chars=35)
    
    # Construcción del bloque de texto según si tiene 1 o 2 líneas
    if line2:
        title_svg = f'''<text x="0" y="0" class="yt-title">{line1}</text>
      <text x="0" y="24" class="yt-title">{line2}</text>'''
        channel_y = 48
        meta_y = 68
    else:
        title_svg = f'''<text x="0" y="0" class="yt-title">{line1}</text>'''
        channel_y = 25
        meta_y = 46

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <clipPath id="thumbClip_{index}">
      <rect x="0" y="0" width="{w}" height="326" rx="14"/>
    </clipPath>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&amp;display=swap');
      .yt-title {{ font-family: 'Roboto', -apple-system, sans-serif; font-weight: 600; font-size: 19px; fill: #F1F1F1; }}
      .yt-channel {{ font-family: 'Roboto', -apple-system, sans-serif; font-weight: 500; font-size: 14.5px; fill: #AAAAAA; }}
      .yt-meta {{ font-family: 'Roboto', -apple-system, sans-serif; font-size: 14px; fill: #AAAAAA; }}
      .yt-time {{ font-family: 'Roboto', sans-serif; font-weight: 700; font-size: 13px; fill: #FFFFFF; letter-spacing: 0.5px; }}
    </style>
  </defs>

  <!-- Dark Background (seamless with GitHub Dark mode) -->
  <rect width="{w}" height="{h}" fill="#0F0F0F" rx="16"/>

  <!-- Thumbnail (16:9) with rounded corners -->
  <g clip-path="url(#thumbClip_{index})">
    <image href="data:image/{mime_type};base64,{b64_thumb}" x="0" y="0" width="{w}" height="326" preserveAspectRatio="xMidYMid slice"/>
  </g>

  <!-- Duration Badge (bottom-right of thumbnail) -->
  <g transform="translate({badge_x}, {badge_y})">
    <rect x="-6" y="-13" width="60" height="23" rx="4" fill="rgba(0,0,0,0.85)"/>
    <text x="24" y="3" text-anchor="middle" class="yt-time">{video["duration"]}</text>
  </g>

  <!-- Info Area below thumbnail -->
  <g transform="translate(12, 345)">
    <!-- Channel Avatar Circle -->
    <g transform="translate(22, 22)">
      <circle cx="0" cy="0" r="22" fill="#241352"/>
      <clipPath id="avatarClip_{index}">
        <circle cx="0" cy="0" r="22"/>
      </clipPath>
      <image href="data:image/png;base64,{b64_avatar}" x="-22" y="-22" width="44" height="44" clip-path="url(#avatarClip_{index})"/>
    </g>

    <!-- Details -->
    <g transform="translate(58, 14)">
      <!-- Title (1 or 2 lines) -->
      {title_svg}
      
      <!-- Channel name + Verified checkmark -->
      <g transform="translate(0, {channel_y})">
        <text x="0" y="0" class="yt-channel">{CHANNEL_NAME}</text>
        <g transform="translate(72, -13) scale(0.65)" fill="#AAAAAA">
          <path d="{check_path}"/>
        </g>
      </g>
      
      <!-- Views & Date -->
      <text x="0" y="{meta_y}" class="yt-meta">{video["views"]}</text>
    </g>

    <!-- 3 Dots Menu Icon on Right -->
    <g transform="translate({w - 32}, 16)" fill="#AAAAAA">
      <circle cx="0" cy="0" r="2"/>
      <circle cx="0" cy="6" r="2"/>
      <circle cx="0" cy="12" r="2"/>
    </g>
  </g>
</svg>'''

    out_file = os.path.join(SVG_DIR, f"yt_card_{index}.svg")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] Generada tarjeta: {out_file} - {video['title']}")

def main():
    print("==================================================")
    print("  GENERANDO TARJETAS YOUTUBE CON SOPORTE 2 LÍNEAS")
    print("==================================================")
    b64_avatar = get_base64_avatar()
    for idx, video in enumerate(VIDEOS, start=1):
        print(f"\n[>] Procesando video {idx}: {video['id']}")
        update_video_stats(video)
        generate_card(video, idx, b64_avatar)
    print("\nTodas las tarjetas han sido actualizadas con exito en assets/svg/!")

if __name__ == "__main__":
    main()
