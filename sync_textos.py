#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPILADOR DE PLANTILLAS Y SINCRONIZADOR DE TEXTOS: textos_talentopolis.txt -> index.html
Sincroniza y compila de forma robusta y portable todo el contenido del sitio web.
"""

import os
import re
import html as html_sanitizer
import sys


# Configuración de rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_FILE = os.path.join(BASE_DIR, "textos_talentopolis.txt")
TEMPLATE_FILE = os.path.join(BASE_DIR, "index.template.html")
HTML_FILE = os.path.join(BASE_DIR, "index.html")
BACKUP_FILE = os.path.join(BASE_DIR, "index_backup.html")

# Diccionarios estáticos de mapeo de recursos multimedia para mantener fidelidad estética
SERVICE_ICONS = [
    "🎙️", "🎥", "🎧", "📡", "🤝", "📢", "💡", "📱"
]

DELIVERABLE_ICONS = [
    "🎬", "📱", "📋", "🎨", "🎛️", "🚀"
]

def get_showcase_img(title):
    t = title.lower()
    if "maza" in t:
        return "assets/caratula_capitulos_destacados/maza_youtube.jpg"
    elif "quiroga" in t:
        return "assets/caratula_capitulos_destacados/quiroga_youtube.jpg"
    elif "ackerman" in t:
        return "assets/caratula_capitulos_destacados/ackerman_youtube.jpg"
    elif "mujer sin pausa" in t:
        return "assets/caratula_capitulos_destacados/mujersinpausa.webp"
    elif "ramon" in t or "heredia" in t:
        return "assets/caratula_capitulos_destacados/ramon_heredia.jpg"
    elif "mewes" in t:
        return "assets/caratula_capitulos_destacados/mewes.jpg"
    return "assets/caratula_capitulos_destacados/maza_youtube.jpg"

def get_program_logo(title):
    t = title.lower()
    if "organizaciones" in t:
        return "assets/Logo_PodCast/Logo_ODM.png"
    elif "aula" in t:
        return "assets/Logo_PodCast/Logo_aula_T1.png"
    elif "mujeres sin" in t or "mujer sin" in t:
        return "assets/Logo_PodCast/Logo_mujersinpausa.png"
    elif "coffeebreak" in t or "coffee" in t:
        return "assets/Logo_PodCast/Logo_coffe.png"
    elif "mujer hoy" in t or "sin límites" in t or "sin limites" in t:
        return "assets/Logo_PodCast/1108f409-ad83-450f-9ea1-2f7a2d391a04.png"
    elif "conocimiento" in t:
        return "assets/Logo_PodCast/Logo_conocimientoencapsulado.png"
    elif "kolumna" in t:
        return "assets/Logo_PodCast/Logo_kolumna_laboral.png"
    elif "ciso" in t:
        return "assets/Logo_PodCast/logo_CISOs.png"
    elif "finanzas" in t:
        return "assets/Logo_PodCast/logo_FF.png"
    return "assets/Logo_PodCast/Logo_ODM.png"

def get_program_link(title):
    t = title.lower()
    if "organizaciones" in t:
        return "https://www.youtube.com/playlist?list=PLRS8xZ-8eLGV0eJxIB-22XfPBITFTw5Jp"
    elif "aula" in t:
        return "https://www.youtube.com/playlist?list=PLRS8xZ-8eLGUCva5MHsaa5W9ygDXw_EpP"
    elif "mujeres sin" in t or "mujer sin" in t:
        return "https://www.youtube.com/playlist?list=PLRS8xZ-8eLGWF8sMDm_bvUyyYoxnnxQGE"
    elif "coffeebreak" in t or "coffee" in t:
        return "https://www.youtube.com/playlist?list=PLRS8xZ-8eLGW-9lppsR7_uKmi3mRqcwW7"
    elif "mujer hoy" in t or "sin límites" in t or "sin limites" in t:
        return "https://www.youtube.com/playlist?list=PLRS8xZ-8eLGWF8sMDm_bvUyyYoxnnxQGE"
    elif "conocimiento" in t:
        return "https://www.youtube.com/watch?v=JHYZmTMU3LA&list=PLRS8xZ-8eLGWEO39t0W6iuPP8_6vSMxCL"
    elif "kolumna" in t:
        return "https://www.youtube.com/playlist?list=PLRS8xZ-8eLGXRY2f1hMiyhKhDCWkEqNMr"
    elif "ciso" in t:
        return "https://www.youtube.com/playlist?list=PLRS8xZ-8eLGWS5UtKPRg8jWuWHkZRgafF"
    elif "finanzas" in t:
        return "https://www.youtube.com/playlist?list=PLRS8xZ-8eLGU3DYqTiZo_Aabjxl0mQLGw"
    return "https://www.youtube.com/@talentopolis"

def get_guest_img(name):
    n = name.lower()
    if "rincón" in n or "rincon" in n:
        return "assets/fotos_invitado_comunicarte/foto-rincon.png"
    elif "melo" in n:
        return "assets/fotos_invitado_comunicarte/foto-melo.png"
    elif "daza" in n:
        return "assets/fotos_invitado_comunicarte/foto-daza.png"
    elif "quiroga" in n:
        return "assets/quiroga_youtube.jpg"
    elif "mewes" in n:
        return "assets/mewes.jpg"
    return "assets/fotos_invitado_comunicarte/foto-rincon.png"

def get_spotify_img(name):
    n = name.lower()
    if "organizaciones" in n:
        return "assets/caratula_spotify_programas/Spotify_ODM.jpg"
    elif "aula" in n:
        return "assets/caratula_spotify_programas/Spotify_Aula.jpg"
    elif "coffee" in n:
        return "assets/caratula_spotify_programas/Spotify_Cofebreak.jpg"
    elif "mujer" in n or "límite" in n or "limite" in n:
        return "assets/caratula_spotify_programas/Spotify_Mujersinlimites.jpg"
    return "assets/caratula_spotify_programas/Spotify_ODM.jpg"

def get_spotify_link(name):
    n = name.lower()
    if "organizaciones" in n:
        return "https://talentopolis.cl/organizaciones-del-manana-podcast/?playlist=5f72368&video=b88beb4"
    elif "aula" in n:
        return "https://talentopolis.cl/delaulaalacancha-podcast/"
    elif "coffee" in n:
        return "https://talentopolis.cl/coffeebreak-con-talento/"
    elif "mujer" in n or "límite" in n or "limite" in n:
        return "https://talentopolis.cl/mujeres-sin-pausa-podcast/"
    return "https://open.spotify.com/show/4C5OdIj2KqmfY1ij7VkTiG"

def get_member_img(name):
    n = name.lower()
    if "andrés" in n or "andres" in n:
        return "assets/fotos_equipo/foto-andres.png"
    elif "claudina" in n:
        return "assets/fotos_equipo/foto-claudina.png"
    elif "lucas" in n:
        return "assets/fotos_equipo/foto-lucas.png"
    elif "freddy" in n:
        return "assets/fotos_equipo/foto-freddy.png"
    return "assets/fotos_equipo/foto-andres.png"

def log(msg):
    print(f"[*] {msg}")

def safe_escape(text):
    if not text:
        return ""
    return html_sanitizer.escape(text)

def format_highlights(text):
    """Convierte [texto] en <span class='section-highlight'>texto</span>"""
    if not text:
        return ""
    return re.sub(r'\[(.*?)\]', r'<span class="section-highlight">\1</span>', text)

def parse_textos():
    log(f"Leyendo textos desde {TXT_FILE}...")
    if not os.path.exists(TXT_FILE):
        raise FileNotFoundError(f"No se encontró el archivo de textos en: {TXT_FILE}")
        
    with open(TXT_FILE, 'r', encoding='utf-8') as f:
        content = f.read().replace('\r\n', '\n')
        
    # Separar el documento por páginas
    pages_raw = re.split(r'### PÁGINA \d+:\s*', content)
    
    # Debe haber 12 páginas más el prefacio inicial
    if len(pages_raw) < 13:
        raise ValueError(f"El archivo TXT debe contener las 12 páginas estructuradas con '### PÁGINA X:'. Encontradas: {len(pages_raw)-1}")
        
    # Inicializar diccionarios de datos para la plantilla
    p_data = {}
    
    # ── PÁGINA 1: HERO ──
    hero_txt = pages_raw[1].strip()
    hero_kv = {}
    for line in hero_txt.split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            hero_kv[k.strip().upper()] = v.strip()
    p_data['HERO_TAGLINE'] = format_highlights(safe_escape(hero_kv.get('TAGLINE', '')))
    p_data['HERO_TÍTULO'] = format_highlights(safe_escape(hero_kv.get('TÍTULO', '')))
    p_data['HERO_SUBTÍTULO'] = format_highlights(safe_escape(hero_kv.get('SUBTÍTULO', '')))
    
    # ── PÁGINA 2: ABOUT (Quiénes Somos) ──
    about_txt = pages_raw[2].strip()
    about_kv = {}
    metrics_list = []
    in_metrics = False
    
    for line in about_txt.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('MÉTRICAS:'):
            in_metrics = True
            continue
        if line.startswith('REDES SOCIALES:'):
            in_metrics = False
            continue
        if in_metrics:
            m_match = re.match(r'^\d+\.\s*(.*)', line)
            if m_match:
                metrics_list.append(m_match.group(1).strip())
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            about_kv[k.strip().upper()] = v.strip()
            
    p_data['ABOUT_TÍTULO'] = format_highlights(safe_escape(about_kv.get('TÍTULO', '')))
    p_data['ABOUT_PÁRRAFO_1'] = format_highlights(safe_escape(about_kv.get('PÁRRAFO 1', '')))
    p_data['ABOUT_PÁRRAFO_2'] = format_highlights(safe_escape(about_kv.get('PÁRRAFO 2', '')))
    
    # Procesar la lista estructurada de MÉTRICAS
    p_data['ABOUT_METRICAS'] = []
    for i, item in enumerate(metrics_list[:6]):
        parts = item.split(' — ', 1)
        if len(parts) != 2:
            parts = item.split(' - ', 1)
        if len(parts) == 2:
            val, label = parts[0].strip(), parts[1].strip()
        else:
            val, label = item, ""
        p_data['ABOUT_METRICAS'].append({
            'METRIC_VALUE': safe_escape(val),
            'METRIC_LABEL': safe_escape(label),
            'METRIC_ACCENT': " accent" if i % 2 != 0 else ""
        })
        
    # ── PÁGINA 3: SERVICIOS ──
    servicios_txt = pages_raw[3].strip()
    servicios_kv = {}
    servicios_list = []
    deliverables_list = []
    in_listado = False
    in_deliv = False
    
    for line in servicios_txt.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('LISTADO'):
            in_listado = True
            in_deliv = False
            continue
        if line.startswith('LO QUE RECIBE EL CLIENTE:'):
            in_listado = False
            in_deliv = True
            continue
        if in_listado:
            s_match = re.match(r'^\d+\.\s*(.*)', line)
            if s_match:
                servicios_list.append(s_match.group(1).strip())
            continue
        if in_deliv:
            # Limpiar viñetas
            clean_item = re.sub(r'^-\s*(?:✅\s*)?', '', line).strip()
            if clean_item:
                deliverables_list.append(clean_item)
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            servicios_kv[k.strip().upper()] = v.strip()
            
    p_data['SERVICES_TÍTULO'] = format_highlights(safe_escape(servicios_kv.get('TÍTULO', '')))
    p_data['SERVICES_SUBTÍTULO'] = format_highlights(safe_escape(servicios_kv.get('SUBTÍTULO', '')))
    
    # Procesar GRID de Servicios
    p_data['SERVICES_LIST'] = []
    for i, item in enumerate(servicios_list[:8]):
        parts = item.split(':', 1)
        s_title = parts[0].strip()
        s_desc = parts[1].strip() if len(parts) > 1 else ""
        icon = SERVICE_ICONS[i] if i < len(SERVICE_ICONS) else "🎙️"
        p_data['SERVICES_LIST'].append({
            'SERVICE_ICON': icon,
            'SERVICE_TITLE': safe_escape(s_title),
            'SERVICE_DESC': safe_escape(s_desc)
        })
        
    # Procesar Entregables que recibe tu marca
    p_data['DELIVERABLES'] = []
    for i, item in enumerate(deliverables_list[:6]):
        title = ""
        desc = ""
        if " (" in item:
            title, desc = item.split(" (", 1)
            desc = desc.rstrip(")").replace("/", " / ")
        elif " y " in item:
            title, desc = item.split(" y ", 1)
            desc = "y " + desc
        else:
            title = item
            desc = ""
            
        icon = DELIVERABLE_ICONS[i] if i < len(DELIVERABLE_ICONS) else "🎬"
        p_data['DELIVERABLES'].append({
            'DLV_ICON': icon,
            'DLV_TITLE': safe_escape(title),
            'DLV_DESC': safe_escape(desc)
        })
        
    # ── PÁGINA 4: PROCESO (Workflow) ──
    workflow_txt = pages_raw[4].strip()
    workflow_kv = {}
    steps_dict = {}
    in_steps = False
    
    for line in workflow_txt.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('PASOS'):
            in_steps = True
            continue
        if in_steps:
            st_match = re.match(r'^(\d+)\.\s*(.*)', line)
            if st_match:
                st_num = int(st_match.group(1))
                st_content = st_match.group(2).strip()
                parts = st_content.split(':', 1)
                st_title = parts[0].strip()
                st_desc = parts[1].strip() if len(parts) > 1 else ""
                steps_dict[st_num] = {
                    'title': st_title,
                    'desc': st_desc
                }
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            workflow_kv[k.strip().upper()] = v.strip()
            
    p_data['WORKFLOW_TÍTULO'] = format_highlights(safe_escape(workflow_kv.get('TÍTULO', '')))
    p_data['WORKFLOW_SUBTÍTULO'] = format_highlights(safe_escape(workflow_kv.get('SUBTÍTULO', '')))
    
    # Mapear los 6 pasos al diccionario plano
    for num in range(1, 7):
        step_info = steps_dict.get(num, {'title': f"Paso {num}", 'desc': ""})
        p_data[f'WORKFLOW_STEP{num}_TITLE'] = safe_escape(step_info['title'])
        p_data[f'WORKFLOW_STEP{num}_DESC'] = safe_escape(step_info['desc'])
        
    # ── PÁGINA 5: GALERÍA DE VIDEOS (Brochure Carrusel) ──
    vg_txt = pages_raw[5].strip()
    vg_kv = {}
    vg_urls = []
    in_vg_videos = False
    
    for line in vg_txt.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('VIDEOS'):
            in_vg_videos = True
            continue
        if in_vg_videos:
            v_match = re.match(r'^\d+\.\s*(.*)', line)
            if v_match:
                vg_urls.append(v_match.group(1).strip())
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            vg_kv[k.strip().upper()] = v.strip()
            
    p_data['VIDEOGALLERY_TÍTULO'] = format_highlights(safe_escape(vg_kv.get('TÍTULO', '')))
    p_data['VIDEOGALLERY_TAGLINE'] = format_highlights(safe_escape(vg_kv.get('TAGLINE', '')))
    
    # Slides y dots para la galería de videos
    p_data['VIDEO_GALLERY_SLIDES'] = []
    p_data['VIDEO_GALLERY_DOTS'] = []
    for i, url in enumerate(vg_urls[:6]):
        video_id = url.split('/')[-1].split('?')[0]
        p_data['VIDEO_GALLERY_SLIDES'].append({
            'VIDEO_URL': url,
            'VIDEO_ID': video_id,
            'VIDEO_INDEX': str(i + 1)
        })
        p_data['VIDEO_GALLERY_DOTS'].append({
            'VG_DOT_ACTIVE': " active" if i == 0 else ""
        })
        
    # ── PÁGINA 6: SHOWCASE (Producciones Destacadas) ──
    showcase_txt = pages_raw[6].strip()
    showcase_kv = {}
    showcase_videos = []
    lines = showcase_txt.split('\n')
    idx = 0
    in_sc_videos = False
    
    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue
        if line.startswith('VIDEOS'):
            in_sc_videos = True
            idx += 1
            continue
        if in_sc_videos:
            v_match = re.match(r'^\d+\.\s*(.*)', line)
            if v_match:
                full_sc_title = v_match.group(1).strip()
                
                # Buscar la URL en la siguiente línea
                sc_url = ""
                j = idx + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if next_line.startswith('URL:'):
                        sc_url = next_line.split('URL:', 1)[1].strip()
                        break
                    elif next_line:
                        # Si encontramos otra cosa, frenar
                        break
                    j += 1
                
                parts = full_sc_title.split(' — ', 1)
                if len(parts) != 2:
                    parts = full_sc_title.split(' - ', 1)
                sc_title = parts[0].strip()
                sc_program = parts[1].strip() if len(parts) == 2 else ""
                
                showcase_videos.append({
                    'title': sc_title,
                    'program': sc_program,
                    'url': sc_url
                })
                idx = j
            idx += 1
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            showcase_kv[k.strip().upper()] = v.strip()
        idx += 1
        
    p_data['SHOWCASE_TÍTULO'] = format_highlights(safe_escape(showcase_kv.get('TÍTULO', '')))
    p_data['SHOWCASE_SUBTÍTULO'] = format_highlights(safe_escape(showcase_kv.get('SUBTÍTULO', '')))
    
    p_data['SHOWCASE_LIST'] = []
    for item in showcase_videos[:6]:
        p_data['SHOWCASE_LIST'].append({
            'SHOWCASE_URL': item['url'],
            'SHOWCASE_TITLE': safe_escape(item['title']),
            'SHOWCASE_SUB': safe_escape(item['program']),
            'SHOWCASE_IMG': get_showcase_img(item['title']),
            'SHOWCASE_ALT': safe_escape(item['title'])
        })
        
    # ── PÁGINA 7: PROGRAMAS ──
    programs_txt = pages_raw[7].strip()
    programs_kv = {}
    programs_list = []
    in_pg_list = False
    
    for line in programs_txt.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('LISTADO'):
            in_pg_list = True
            continue
        if in_pg_list:
            p_match = re.match(r'^\d+\.\s*(.*)', line)
            if p_match:
                full_text = p_match.group(1).strip()
                parts = full_text.split(':', 1)
                p_title = parts[0].strip()
                p_desc = parts[1].strip() if len(parts) > 1 else ""
                programs_list.append({
                    'title': p_title,
                    'desc': p_desc
                })
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            programs_kv[k.strip().upper()] = v.strip()
            
    p_data['PROGRAMS_TÍTULO'] = format_highlights(safe_escape(programs_kv.get('TÍTULO', '')))
    p_data['PROGRAMS_SUBTÍTULO'] = format_highlights(safe_escape(programs_kv.get('SUBTÍTULO', '')))
    
    p_data['PROGRAM_LIST'] = []
    for item in programs_list[:9]:
        title_str = item['title']
        highlight_match = re.search(r'\s+((?:T|TT)\d+-\d+)$', title_str)
        if highlight_match:
            highlight = highlight_match.group(1)
            base_title = title_str[:highlight_match.start()].strip()
        else:
            highlight = ""
            base_title = title_str
            
        p_data['PROGRAM_LIST'].append({
            'PROGRAM_LINK': get_program_link(base_title),
            'PROGRAM_LOGO': get_program_logo(base_title),
            'PROGRAM_ALT': safe_escape(base_title),
            'PROGRAM_TITLE': safe_escape(base_title),
            'PROGRAM_HIGHLIGHT': highlight,
            'PROGRAM_DESC': safe_escape(item['desc'])
        })
        
    # ── PÁGINA 8: COMUNICARTE ──
    comunicarte_txt = pages_raw[8].strip()
    comunicarte_kv = {}
    guests_list = []
    lines = comunicarte_txt.split('\n')
    idx = 0
    in_guests = False
    
    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue
        if line.startswith('INVITADOS'):
            in_guests = True
            idx += 1
            continue
        if in_guests:
            g_match = re.match(r'^\d+\.\s*(.*)', line)
            if g_match:
                g_name = g_match.group(1).strip()
                g_role = ""
                g_desc = ""
                
                j = idx + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if next_line.startswith('Cargo:'):
                        g_role = next_line.split('Cargo:', 1)[1].strip()
                    elif next_line.startswith('Descripción:'):
                        g_desc = next_line.split('Descripción:', 1)[1].strip()
                    elif next_line:
                        if re.match(r'^\d+\.', next_line) or next_line.startswith('==='):
                            break
                    j += 1
                    
                guests_list.append({
                    'name': g_name,
                    'role': g_role,
                    'desc': g_desc
                })
                idx = j
                continue
            idx += 1
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            comunicarte_kv[k.strip().upper()] = v.strip()
        idx += 1
        
    p_data['COMUNICARTE_TÍTULO'] = format_highlights(safe_escape(comunicarte_kv.get('TÍTULO', '')))
    p_data['COMUNICARTE_DESCRIPCIÓN'] = format_highlights(safe_escape(comunicarte_kv.get('DESCRIPCIÓN', '')))
    
    p_data['COMUNICARTE_GUESTS'] = []
    for item in guests_list[:3]:
        p_data['COMUNICARTE_GUESTS'].append({
            'GUEST_IMG': get_guest_img(item['name']),
            'GUEST_NAME': safe_escape(item['name']),
            'GUEST_ROLE': safe_escape(item['role']),
            'GUEST_DESC': safe_escape(item['desc'])
        })
        
    # ── PÁGINA 9: GALERÍA DE INVITADOS ──
    guests_gallery_txt = pages_raw[9].strip()
    gg_kv = {}
    for line in guests_gallery_txt.split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            gg_kv[k.strip().upper()] = v.strip()
    p_data['GUESTSGALLERY_TÍTULO'] = format_highlights(safe_escape(gg_kv.get('TÍTULO', '')))
    p_data['GUESTSGALLERY_BAJADA'] = format_highlights(safe_escape(gg_kv.get('BAJADA', '')))
    
    # ── PÁGINA 10: SPOTIFY ──
    spotify_txt = pages_raw[10].strip()
    spotify_kv = {}
    spotify_programs = []
    in_sp_programs = False
    
    for line in spotify_txt.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('PROGRAMAS'):
            in_sp_programs = True
            continue
        if in_sp_programs:
            s_match = re.match(r'^\d+\.\s*(.*)', line)
            if s_match:
                spotify_programs.append(s_match.group(1).strip())
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            spotify_kv[k.strip().upper()] = v.strip()
            
    p_data['SPOTIFY_TÍTULO'] = format_highlights(safe_escape(spotify_kv.get('TÍTULO', '')))
    p_data['SPOTIFY_SUBTÍTULO'] = format_highlights(safe_escape(spotify_kv.get('SUBTÍTULO', '')))
    
    p_data['SPOTIFY_LIST'] = []
    for item in spotify_programs[:4]:
        p_data['SPOTIFY_LIST'].append({
            'SPOTIFY_URL': get_spotify_link(item),
            'SPOTIFY_IMG': get_spotify_img(item),
            'SPOTIFY_ALT': safe_escape(item)
        })
        
    # ── PÁGINA 11: EQUIPO ──
    equipo_txt = pages_raw[11].strip()
    equipo_kv = {}
    team_members = []
    in_members = False
    
    for line in equipo_txt.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('INTEGRANTES'):
            in_members = True
            continue
        if line.startswith('BANNER PARTNERS:'):
            in_members = False
            continue
        if in_members:
            m_match = re.match(r'^\d+\.\s*(.*)', line)
            if m_match:
                full_member = m_match.group(1).strip()
                parts = re.split(r'\s*—\s*|\s*-\s*', full_member)
                name = parts[0].strip() if len(parts) > 0 else ""
                role = parts[1].strip() if len(parts) > 1 else ""
                link = parts[2].strip() if len(parts) > 2 else ""
                
                team_members.append({
                    'name': name,
                    'role': role,
                    'link': link
                })
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            equipo_kv[k.strip().upper()] = v.strip()
            
    p_data['EQUIPO_TÍTULO'] = format_highlights(safe_escape(equipo_kv.get('TÍTULO', '')))
    
    p_data['EQUIPO_LIST'] = []
    for item in team_members[:4]:
        member_link = item['link']
        if member_link and not member_link.startswith('http'):
            member_link = 'https://' + member_link
        p_data['EQUIPO_LIST'].append({
            'MEMBER_LINK': member_link,
            'MEMBER_IMG': get_member_img(item['name']),
            'MEMBER_NAME': safe_escape(item['name']),
            'MEMBER_ROLE': safe_escape(item['role'])
        })
        
    # ── PÁGINA 12: CONTACTO ──
    contacto_txt = pages_raw[12].strip()
    contacto_kv = {}
    footer_datos = {}
    in_datos = False
    
    for line in contacto_txt.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('FOOTER — DATOS DE CONTACTO:'):
            in_datos = True
            continue
        if line.startswith('FOOTER — MARCA:'):
            in_datos = False
            continue
        if in_datos:
            clean_item = re.sub(r'^-\s*', '', line).strip()
            if ':' in clean_item:
                k, v = clean_item.split(':', 1)
                # Extraer texto antes del enlace en paréntesis
                val = v.split('(', 1)[0].strip()
                footer_datos[k.strip().upper()] = val
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            contacto_kv[k.strip().upper()] = v.strip()
        elif line.startswith('Productora audiovisual'):
            contacto_kv['MARCA'] = line
            
    p_data['CONTACTO_CTA'] = format_highlights(safe_escape(contacto_kv.get('CTA', '')))
    p_data['CONTACTO_SUB_CTA'] = format_highlights(safe_escape(contacto_kv.get('SUB-CTA', '')))
    p_data['CONTACTO_MARCA'] = safe_escape(contacto_kv.get('MARCA', ''))
    
    p_data['CONTACTO_WHATSAPP'] = safe_escape(footer_datos.get('WHATSAPP', ''))
    p_data['CONTACTO_EMAIL'] = safe_escape(footer_datos.get('EMAIL', ''))
    
    raw_addr = footer_datos.get('DIRECCIÓN', footer_datos.get('DIRECCION', ''))
    # Formatear dirección para conservar el salto de línea premium en Providencia
    p_data['CONTACTO_DIRECCION'] = safe_escape(raw_addr).replace(', Providencia', '<br>Providencia')
    
    p_data['CONTACTO_COPYRIGHT'] = safe_escape(contacto_kv.get('COPYRIGHT', ''))
    
    return p_data

def compile_template(variables):
    log(f"Compilando plantilla desde {TEMPLATE_FILE}...")
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(f"No se encontró el archivo plantilla en: {TEMPLATE_FILE}")
        
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
        
    # 1. Reemplazar los bloques dinámicos (loops)
    blocks = [
        'ABOUT_METRICAS',
        'SERVICES_LIST',
        'DELIVERABLES',
        'VIDEO_GALLERY_SLIDES',
        'VIDEO_GALLERY_DOTS',
        'SHOWCASE_LIST',
        'PROGRAM_LIST',
        'COMUNICARTE_GUESTS',
        'SPOTIFY_LIST',
        'EQUIPO_LIST'
    ]
    
    for block_name in blocks:
        pattern = rf"<!--\s*BEGIN\s+{block_name}\s*-->([\s\S]*?)<!--\s*END\s+{block_name}\s*-->"
        match = re.search(pattern, html)
        
        if not match:
            log(f"[ADVERTENCIA] No se encontró el bloque dinámico '{block_name}' en la plantilla.")
            continue
            
        block_template = match.group(1)
        items_data = variables.get(block_name, [])
        rendered_items = []
        
        for item in items_data:
            rendered = block_template
            for k, v in item.items():
                rendered = rendered.replace(f"{{{{ {k} }}}}", str(v))
            rendered_items.append(rendered)
            
        rendered_block_html = "".join(rendered_items)
        html = re.sub(pattern, rendered_block_html, html)
        
    # 2. Reemplazar las variables individuales de texto plano
    for key, value in variables.items():
        if isinstance(value, str):
            html = html.replace(f"{{{{ {key} }}}}", value)
            
    return html

def main():
    log("Iniciando compilador y sincronizador de textos...")
    try:
        # 1. Parsear el archivo de textos
        parsed_variables = parse_textos()
        log("Parsea completado con éxito de todos los textos comerciales.")
        
        # 2. Leer index.html actual (si existe) para respaldo
        if os.path.exists(HTML_FILE):
            log(f"Creando respaldo en {BACKUP_FILE}...")
            with open(HTML_FILE, 'r', encoding='utf-8') as f:
                current_html = f.read()
            with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
                f.write(current_html)
                
        # 3. Compilar la plantilla
        compiled_html = compile_template(parsed_variables)
        
        # 4. Escribir el nuevo archivo compilado index.html
        log(f"Escribiendo resultado compilado en {HTML_FILE}...")
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(compiled_html)
            
        log("¡Felicidades! La sincronización y compilación del HTML fue 100% exitosa.")
        
    except Exception as e:
        log(f"ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
