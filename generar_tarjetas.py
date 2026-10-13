"""
=============================================================================
GENERADOR Y ACTUALIZADOR AUTOMÁTICO DE TARJETAS DE YOUTUBE PARA ETERNODEV
=============================================================================
Este script:
1. Permite actualizar de forma 100% automática las visitas y fecha relativa
   de los vídeos conectándose a YouTube sin necesidad de API keys.
2. Genera los archivos SVG (yt_card_1.svg, yt_card_2.svg, etc.) con el diseño
   idéntico al feed oficial de YouTube.
3. Permite añadir nuevos vídeos en el array VIDEOS.
4. Puede ejecutarse manualmente o de forma programada diaria mediante GitHub Actions.
=============================================================================
"""

import os
import urllib.request
import base64
import json
import re
from PIL import Image

CHANNEL_NAME = "EternoDev"
AVATAR_PATH = "logo.png"

# Lista de vídeos a mostrar en el feed (puedes añadir o cambiar los que quieras)
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

def update_video_stats(video):
    """Obtiene de forma dinámica las visualizaciones y fecha en tiempo real"""
    vid_id = video["id"]
    try:
        url = f"https://www.youtube.com/watch?v={vid_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
        
        # 1. Short view count text
        sv = re.findall(r'"shortViewCount":\{"simpleText":"([^"]+)"', html)
        views_str = sv[0] if sv else None
        
        # 2. Date text (ej: hace 1 mes)
        dt = re.findall(r'"dateText":\{"simpleText":"([^"]+)"', html)
        date_str = dt[0] if dt else None
        
        if views_str and date_str:
            video["views"] = f"{views_str} • {date_str}"
            print(f"  [+] Datos actualizados en vivo para {vid_id}: {video['views']}")
        elif views_str:
            # mantener parte de la fecha existente
            old_parts = video["views"].split("•")
            time_part = old_parts[1].strip() if len(old_parts) > 1 else ""
            video["views"] = f"{views_str} • {time_part}"
            print(f"  [+] Visitas actualizadas en vivo para {vid_id}: {video['views']}")
    except Exception as e:
        print(f"  [-] Manteniendo datos guardados para {vid_id} ({e})")

def get_base64_avatar():
    if os.path.exists(AVATAR_PATH):
        with open(AVATAR_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def get_base64_thumbnail(video):
    local_file = video.get("thumbnail_file")
    if local_file and os.path.exists(local_file):
        with open(local_file, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8"), "png" if local_file.endswith(".png") else "jpeg"
    
    vid_id = video["id"]
    cache_file = f"thumb_{vid_id}.jpg"
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
    w, h = 580, 440
    b64_thumb, mime_type = get_base64_thumbnail(video)
    
    # Checkmark icon exact YouTube vector
    check_path = "M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.4-1.4 3.6 3.6 7.6-7.6L19 8l-9 9z"

    # Exact adjustments:
    # 1. Badge duration:
    #    Lower on Y and more to the right:
    #    Thumbnail height is 326.
    #    Badge bottom-right placed at x = (w - 12), y = 314 -> transform translate(w - 68, 298)
    #    Duration badge is now beautifully anchored at the bottom-right corner!
    #
    # 2. Verified checkmark:
    #    Before: translate(74, -11). It was too low!
    #    Now: translate(72, -13) with baseline alignment matching the 14.5px font height!

    badge_x = w - 68  # 512
    badge_y = 298     # moved lower and right

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

  <!-- Duration Badge (bottom-right of thumbnail, lower & right) -->
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
      <!-- Title -->
      <text x="0" y="0" class="yt-title">{video["title"]}</text>
      
      <!-- Channel name + Verified checkmark (perfectly aligned with text center) -->
      <g transform="translate(0, 24)">
        <text x="0" y="0" class="yt-channel">{CHANNEL_NAME}</text>
        <g transform="translate(72, -13) scale(0.65)" fill="#AAAAAA">
          <path d="{check_path}"/>
        </g>
      </g>
      
      <!-- Views & Date -->
      <text x="0" y="44" class="yt-meta">{video["views"]}</text>
    </g>

    <!-- 3 Dots Menu Icon on Right -->
    <g transform="translate({w - 32}, 16)" fill="#AAAAAA">
      <circle cx="0" cy="0" r="2"/>
      <circle cx="0" cy="6" r="2"/>
      <circle cx="0" cy="12" r="2"/>
    </g>
  </g>
</svg>'''

    out_file = f"yt_card_{index}.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] Generada tarjeta: {out_file} - {video['title']}")

def main():
    print("==================================================")
    print("  GENERANDO Y ACTUALIZANDO TARJETAS DE YOUTUBE")
    print("==================================================")
    b64_avatar = get_base64_avatar()
    for idx, video in enumerate(VIDEOS, start=1):
        print(f"\n[>] Procesando video {idx}: {video['id']}")
        update_video_stats(video)
        generate_card(video, idx, b64_avatar)
    print("\nTodas las tarjetas han sido actualizadas con exito!")

if __name__ == "__main__":
    main()
