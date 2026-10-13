"""
=============================================================================
GENERADOR AUTOMÁTICO DE TARJETAS DE YOUTUBE PARA EL PERFIL DE GITHUB
EternoDev - @eternodev
=============================================================================
Instrucciones:
1. Asegúrate de tener Python 3 instalado y Pillow (pip install pillow).
2. Añade o edita los vídeos en la lista `VIDEOS` abajo.
3. Si tienes una miniatura personalizada en PNG/JPG, pon su ruta en 'thumbnail_path'
   o déjalo vacío para que la descargue automáticamente de YouTube.
4. Ejecuta:
   python generar_tarjetas.py
5. Las tarjetas se generarán como `yt_card_1.svg`, `yt_card_2.svg`, etc.
=============================================================================
"""

import os
import urllib.request
import base64
import json
from PIL import Image

# Configuración del canal
CHANNEL_NAME = "EternoDev"
AVATAR_PATH = "logo.png"

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

def get_base64_avatar():
    if os.path.exists(AVATAR_PATH):
        with open(AVATAR_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def get_base64_thumbnail(video):
    # Si existe el archivo local de la miniatura, úsalo
    local_file = video.get("thumbnail_file")
    if local_file and os.path.exists(local_file):
        with open(local_file, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8"), "png" if local_file.endswith(".png") else "jpeg"
    
    # Si no, descárgalo automáticamente de YouTube
    vid_id = video["id"]
    cache_file = f"thumb_{vid_id}.jpg"
    if not os.path.exists(cache_file):
        thumb_url = f"https://i.ytimg.com/vi/{vid_id}/maxresdefault.jpg"
        try:
            req = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                with open(cache_file, 'wb') as f:
                    f.write(data)
        except Exception:
            # Fallback a hqdefault
            thumb_url = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
            req = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                with open(cache_file, 'wb') as f:
                    f.write(data)
    
    with open(cache_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8"), "jpeg"

def generate_card(video, index, b64_avatar):
    w, h = 580, 440
    b64_thumb, mime_type = get_base64_thumbnail(video)
    check_path = "M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.4-1.4 3.6 3.6 7.6-7.6L19 8l-9 9z"

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
  <g transform="translate({w - 65}, 290)">
    <rect x="-8" y="-14" width="60" height="24" rx="4" fill="rgba(0,0,0,0.85)"/>
    <text x="22" y="3" text-anchor="middle" class="yt-time">{video["duration"]}</text>
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
      
      <!-- Channel name + Verified checkmark -->
      <g transform="translate(0, 24)">
        <text x="0" y="0" class="yt-channel">{CHANNEL_NAME}</text>
        <g transform="translate(74, -11) scale(0.65)" fill="#AAAAAA">
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
    print("  GENERANDO TARJETAS DE YOUTUBE PARA ETERNODEV")
    print("==================================================")
    b64_avatar = get_base64_avatar()
    for idx, video in enumerate(VIDEOS, start=1):
        generate_card(video, idx, b64_avatar)
    print("\nTodas las tarjetas han sido actualizadas con exito!")

if __name__ == "__main__":
    main()
