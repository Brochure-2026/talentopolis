#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINCRONIZADOR MAESTRO: Textos TXT -> HTML para Talentópolis
Actualiza TODO el contenido del index.html basándose en textos_talentopolis.txt
"""

import re
import os
import sys
import html as html_sanitizer

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_FILE = os.path.join(BASE_DIR, "textos_talentopolis.txt")
HTML_FILE = os.path.join(BASE_DIR, "index.html")
BACKUP_FILE = os.path.join(BASE_DIR, "index_backup.html")

def log(msg):
    print(f"[*] {msg}")

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def parse_txt():
    """Parsea el archivo TXT y devuelve un diccionario estructurado"""
    content = read_file(TXT_FILE)
    # Normalizar saltos de línea
    content = content.replace('\r\n', '\n')
    
    # Dividir por secciones
    sections_raw = re.split(r'### PÁGINA \d+:', content)
    data = {}
    
    # Mapeo de nombres en TXT a IDs internos para el script
    mapping = {
        'HERO': 'HERO',
        'QUIÉNES SOMOS': 'ABOUT',
        'SERVICIOS': 'SERVICES',
        'PROCESO': 'WORKFLOW',
        'GALERÍA DE VIDEOS': 'VIDEO-GALLERY',
        'SHOWCASE': 'SHOWCASE',
        'PROGRAMAS': 'PROGRAMS',
        'COMUNICARTE': 'COMUNICARTE',
        'GALERÍA DE INVITADOS': 'GUESTS-GALLERY',
        'SPOTIFY': 'SPOTIFY',
        'EQUIPO': 'EQUIPO',
        'CONTACTO': 'CONTACTO'
    }
    
    for sect in sections_raw[1:]:
        lines = sect.strip().split('\n')
        if not lines: continue
        
        # El nombre de la sección es la primera línea (ej: HERO, QUIÉNES SOMOS (About)...)
        full_name = lines[0].strip()
        # Limpiar nombre (quitar descripciones entre paréntesis si las hay)
        clean_name = full_name.split('(')[0].strip().upper()
        
        # Intentar mapear el nombre a un ID conocido
        sect_id = clean_name
        for key, val in mapping.items():
            if key in clean_name:
                sect_id = val
                break
        
        sect_data = {'_full_name': full_name, 'lines': [], 'kv': {}, 'lists': {}}
        
        current_list_name = None
        current_list = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('---') or line.startswith('==='):
                continue
            
            # Detectar si es un encabezado de lista (termina en : y no tiene valor después)
            if line.endswith(':') and not any(line.startswith(p) for p in ['1.', '2.', '-']):
                if current_list_name:
                    sect_data['lists'][current_list_name] = current_list
                current_list_name = line[:-1].strip().upper()
                current_list = []
                continue
            
            # Detectar si es un elemento de lista
            list_match = re.match(r'^(\d+\.|-)\s*(.*)', line)
            if list_match:
                current_list.append(list_match.group(2).strip())
                continue
            
            # Detectar pareja Clave: Valor
            if ':' in line:
                key, val = line.split(':', 1)
                sect_data['kv'][key.strip().upper()] = val.strip()
            else:
                sect_data['lines'].append(line)
        
        # Guardar última lista
        if current_list_name:
            sect_data['lists'][current_list_name] = current_list
            
        data[sect_id] = sect_data
        
    return data

def replace_inner(html, selector_regex, new_text, flags=re.DOTALL):
    """Reemplaza el contenido interno de un tag preservando los atributos"""
    # Regex que captura el tag de apertura, el contenido y el tag de cierre
    pattern = r'(<' + selector_regex + r'[^>]*>)(.*?)(</' + selector_regex.split('\\')[-1].split('[')[0].split('.')[0] + r'>)'
    # Esto es complejo para regex puras. Usaremos una aproximación más segura por ID o clase única.
    return re.sub(pattern, rf'\1{new_text}\3', html, flags=flags)

def update_html(html, data):
    """Aplica los cambios al HTML"""
    
    # 1. HERO
    hero = data.get('HERO')
    if hero:
        log("Actualizando HERO...")
        tagline = html_sanitizer.escape(hero["kv"].get("TAGLINE", ""))
        titulo  = html_sanitizer.escape(hero["kv"].get("TÍTULO", ""))
        sub     = html_sanitizer.escape(hero["kv"].get("SUBTÍTULO", ""))
        
        html = re.sub(r'(<p class="hero-tagline[^>]*>).*?(</p>)', rf'\1{tagline}\2', html, flags=re.DOTALL)
        # El título principal tiene un span que queremos preservar. 
        # Si el texto del TXT coincide con el patrón esperado, lo reinsertamos.
        if "para expertos" in titulo:
             titulo = titulo.replace("para expertos", '<span class="section-highlight">para expertos</span>')
             
        html = re.sub(r'(<h1 class="[^"]*hero-heading-main[^>]*>).*?(</h1>)', rf'\1{titulo}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<p class="hero-sub[^>]*>).*?(</p>)', rf'\1{sub}\2', html, flags=re.DOTALL)

    # 2. ABOUT
    about = data.get('ABOUT')
    if about:
        log("Actualizando ABOUT...")
        label = html_sanitizer.escape(about["kv"].get("LABEL", ""))
        html = re.sub(r'(<p class="[^"]*about-section-label[^>]*>).*?(</p>)', rf'\1{label}\2', html, flags=re.DOTALL)
        
        # Título con span preservado
        title = html_sanitizer.escape(about["kv"].get("TÍTULO", ""))
        if "mirada editorial" in title:
            title = title.replace("mirada editorial", '<span class="section-highlight">mirada editorial</span>')
        html = re.sub(r'(<section id="about".*?<h2 class="section-title">).*?(</h2>)', rf'\1{title}\2', html, flags=re.DOTALL)
        
        # Párrafos
        p1 = html_sanitizer.escape(about["kv"].get("PÁRRAFO 1", ""))
        p2 = html_sanitizer.escape(about["kv"].get("PÁRRAFO 2", ""))
        # Reemplazar los dos primeros <p> después del h2 en la sección about
        about_sect_match = re.search(r'<div class="about-text[^>]*>.*?</h2>\s*<p>(.*?)</p>\s*<p>(.*?)</p>', html, flags=re.DOTALL)
        if about_sect_match:
            old_block = about_sect_match.group(0)
            new_block = old_block.replace(about_sect_match.group(1), p1).replace(about_sect_match.group(2), p2)
            html = html.replace(old_block, new_block)
            
        # Métricas
        metrics = about['lists'].get('MÉTRICAS', [])
        stat_cards = re.findall(r'<div class="stat-card[^>]*>.*?</div>', html, flags=re.DOTALL)
        for i, m_text in enumerate(metrics[:6]):
            if i < len(stat_cards):
                # Formato esperado: "Nombre: Valor" o "1. Nombre: Valor"
                parts = m_text.split(':', 1)
                if len(parts) == 2:
                    label = html_sanitizer.escape(parts[0].strip())
                    val = html_sanitizer.escape(parts[1].strip())
                    new_card = f'<div class="stat-card{" accent" if i%2!=0 else ""}"><div class="number">{val}</div><div class="label">{label}</div></div>'
                    html = html.replace(stat_cards[i], new_card)

    # 3. SERVICES
    services = data.get('SERVICES')
    if services:
        log("Actualizando SERVICES...")
        label = html_sanitizer.escape(services["kv"].get("LABEL", ""))
        titulo = html_sanitizer.escape(services["kv"].get("TÍTULO", ""))
        sub = html_sanitizer.escape(services["kv"].get("SUBTÍTULO", ""))
        
        if "impacto" in titulo:
            titulo = titulo.replace("impacto", '<span class="section-highlight">impacto</span>')

        html = re.sub(r'(<section id="services".*?<p class="section-label">).*?(</p>)', rf'\1{label}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<section id="services".*?<h2 class="section-title">).*?(</h2>)', rf'\1{titulo}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<section id="services".*?<p class="section-sub[^>]*>).*?(</p>)', rf'\1{sub}\2', html, flags=re.DOTALL)
        
        # Grid de servicios
        items = services['lists'].get('LISTADO', [])
        cards = re.findall(r'<div class="service-card[^>]*>.*?</div>', html, flags=re.DOTALL)
        for i, item in enumerate(items[:8]):
            if i < len(cards):
                parts = item.split(':', 1)
                if len(parts) == 2:
                    s_title = html_sanitizer.escape(parts[0].strip())
                    s_desc = html_sanitizer.escape(parts[1].strip())
                    # Preservar el icono (emoji)
                    icon_match = re.search(r'<div class="service-icon">(.*?)</div>', cards[i])
                    icon = icon_match.group(1) if icon_match else "🎙️"
                    new_card = f'<div class="service-card fade-up">\n        <div class="service-icon">{icon}</div>\n        <h3>{s_title}</h3>\n        <p>{s_desc}</p>\n      </div>'
                    html = html.replace(cards[i], new_card)
        
        # Entregables
        deliverables = services['lists'].get('LO QUE RECIBE EL CLIENTE', [])
        if deliverables:
            d_html = '\n'.join([f'        <div class="deliverable-item">{html_sanitizer.escape(d)}</div>' for d in deliverables])
            html = re.sub(r'(<div class="deliverables-grid">).*?(</div>)', rf'\1\n{d_html}\n      \2', html, flags=re.DOTALL)

    # 4. WORKFLOW
    workflow = data.get('WORKFLOW')
    if workflow:
        log("Actualizando WORKFLOW...")
        html = re.sub(r'(<section id="workflow".*?<p class="section-label">).*?(</p>)', rf'\1{html_sanitizer.escape(workflow["kv"].get("LABEL", ""))}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<section id="workflow".*?<h2 class="section-title">).*?(</h2>)', rf'\1{html_sanitizer.escape(workflow["kv"].get("TÍTULO", ""))}\2', html, flags=re.DOTALL)
        
        steps = workflow['lists'].get('PASOS', [])
        step_divs = re.findall(r'<div class="workflow-step">.*?</div>', html, flags=re.DOTALL)
        # Note: HTML order might be 1,2,3,6,5,4 for layout reasons. We match by number in <h4>
        for step_text in steps:
            parts = step_text.split(':', 1)
            if len(parts) == 2:
                s_title = html_sanitizer.escape(parts[0].strip())
                s_desc = html_sanitizer.escape(parts[1].strip())
                # Find which div has this number
                for div in step_divs:
                    if f'<h4>{s_title}</h4>' in div or f'<h4>{s_title.split(".",1)[-1].strip()}</h4>' in div:
                        new_div = re.sub(r'<p>.*?</p>', f'<p>{s_desc}</p>', div)
                        html = html.replace(div, new_div)

    # 4b. VIDEO-GALLERY (Página 5)
    video_gallery = data.get('VIDEO-GALLERY')
    if video_gallery:
        log("Actualizando VIDEO-GALLERY...")
        html = re.sub(r'(<section id="galeria-videos-brochure".*?<h2 class="section-title">).*?(</h2>)', rf'\1{html_sanitizer.escape(video_gallery["kv"].get("TÍTULO", ""))}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<section id="galeria-videos-brochure".*?<p class="video-gallery-tagline">).*?(</p>)', rf'\1{html_sanitizer.escape(video_gallery["kv"].get("TAGLINE", ""))}\2', html, flags=re.DOTALL)
        
        # Videos (Iframes)
        v_list = video_gallery['lists'].get('VIDEOS', [])
        v_slides = re.findall(r'<div class="gallery-slide-full">.*?</div>', html, flags=re.DOTALL)
        for i, v_url in enumerate(v_list[:6]):
            if i < len(v_slides):
                # Extraer URL si viene en formato "1. URL"
                clean_url = re.sub(r'^\d+\.\s*', '', v_url).strip()
                new_slide = f'<div class="gallery-slide-full"><iframe src="{clean_url}" title="Video {i+1}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
                html = html.replace(v_slides[i], new_slide)

    # 5. SHOWCASE
    showcase = data.get('SHOWCASE')
    if showcase:
        log("Actualizando SHOWCASE...")
        html = re.sub(r'(<section id="videos".*?<p class="section-label">).*?(</p>)', rf'\1{html_sanitizer.escape(showcase["kv"].get("LABEL", ""))}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<section id="videos".*?<h2 class="section-title">).*?(</h2>)', rf'\1{html_sanitizer.escape(showcase["kv"].get("TÍTULO", ""))}\2', html, flags=re.DOTALL)
        
        # Videos grid - solo títulos y subtítulos (URLs son más complejas si cambian)
        v_list = showcase['lists'].get('VIDEOS', [])
        v_cards = re.findall(r'<div class="video-card[^>]*>.*?</div>', html, flags=re.DOTALL)
        # El TXT tiene "Nombre - Programa"
        for i, v_text in enumerate(v_list[:6]):
            if i < len(v_cards):
                if ' - ' in v_text:
                    v_name, v_prog = v_text.split(' - ', 1)
                    # Limpiar número si existe "1. Nombre"
                    v_name = html_sanitizer.escape(re.sub(r'^\d+\.\s*', '', v_name))
                    v_prog = html_sanitizer.escape(v_prog)
                    new_card = v_cards[i]
                    new_card = re.sub(r'<h3><a[^>]*>.*?</a></h3>', f'<h3><a href="#">{v_name}</a></h3>', new_card)
                    new_card = re.sub(r'<p>.*?</p>', f'<p>{v_prog}</p>', new_card)
                    html = html.replace(v_cards[i], new_card)

    # 6. PROGRAMS
    programs = data.get('PROGRAMS')
    if programs:
        log("Actualizando PROGRAMS...")
        html = re.sub(r'(<section id="programs".*?<h2 class="section-title">).*?(</h2>)', rf'\1{html_sanitizer.escape(programs["kv"].get("TÍTULO", ""))}\2', html, flags=re.DOTALL)
        
        p_list = programs['lists'].get('LISTADO DE PROGRAMAS', [])
        p_cards = re.findall(r'<a[^>]*class="program-card[^>]*>.*?</a>', html, flags=re.DOTALL)
        for i, p_text in enumerate(p_list[:9]):
            if i < len(p_cards):
                parts = p_text.split(':', 1)
                if len(parts) == 2:
                    p_name = html_sanitizer.escape(re.sub(r'^\d+\.\s*', '', parts[0].strip()))
                    p_desc = html_sanitizer.escape(parts[1].strip())
                    new_card = p_cards[i]
                    # Preservar el highlight si existe (T1-5 etc)
                    highlight = ""
                    h_match = re.search(r'<span class="section-highlight">(.*?)</span>', p_cards[i])
                    if h_match: highlight = f' <span class="section-highlight">{h_match.group(1)}</span>'
                    
                    new_card = re.sub(r'<h3>.*?</h3>', f'<h3>{p_name}{highlight}</h3>', new_card)
                    new_card = re.sub(r'<p>.*?</p>', f'<p>{p_desc}</p>', new_card)
                    html = html.replace(p_cards[i], new_card)

    # 7. COMUNICARTE
    comunicarte = data.get('COMUNICARTE')
    if comunicarte:
        log("Actualizando COMUNICARTE...")
        title = html_sanitizer.escape(comunicarte["kv"].get("TÍTULO", ""))
        desc = html_sanitizer.escape(comunicarte["kv"].get("DESCRIPCIÓN", ""))
        
        if "Próximo Lanzamiento" in title:
            title = title.replace("Próximo Lanzamiento", '<span class="section-highlight">Próximo Lanzamiento</span>')
        html = re.sub(r'(<section id="comunicarte".*?<h2>).*?(</h2>)', rf'\1{title}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<section id="comunicarte".*?<p class="section-sub">).*?(</p>)', rf'\1{desc}\2', html, flags=re.DOTALL)
        
        # Invitados
        guests = comunicarte['lists'].get('INVITADOS DESTACADOS', [])
        g_cards = re.findall(r'<div class="guest-card">.*?</div>\s*</div>', html, flags=re.DOTALL)
        for i, g_text in enumerate(guests[:3]):
            if i < len(g_cards):
                # Formato: "Nombre: Cargo. Descripción."
                parts = g_text.split(':', 1)
                if len(parts) == 2:
                    name = html_sanitizer.escape(parts[0].strip())
                    rest = parts[1].strip()
                    desc_parts = rest.split('. ', 1)
                    cargo = html_sanitizer.escape(desc_parts[0])
                    desc = html_sanitizer.escape(desc_parts[1]) if len(desc_parts) > 1 else ""
                    
                    new_card = g_cards[i]
                    new_card = re.sub(r'<h4>.*?</h4>', f'<h4>{name}</h4>', new_card)
                    # Preservar <br> en cargo si existe
                    cargo_html = cargo.replace(' y ', '<br>')
                    new_card = re.sub(r'<span>.*?</span>', f'<span>{cargo_html}</span>', new_card)
                    new_card = re.sub(r'<p>.*?</p>', f'<p>{desc}</p>', new_card)
                    html = html.replace(g_cards[i], new_card)

    # 7b. GUESTS-GALLERY (Página 9)
    guests_gallery = data.get('GUESTS-GALLERY')
    if guests_gallery:
        log("Actualizando GUESTS-GALLERY...")
        html = re.sub(r'(<section id="galeria-invitados".*?<h2 class="section-title">).*?(</h2>)', rf'\1{html_sanitizer.escape(guests_gallery["kv"].get("TÍTULO", ""))}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<section id="galeria-invitados".*?<p class="section-tagline">).*?(</p>)', rf'\1{html_sanitizer.escape(guests_gallery["kv"].get("BAJADA", ""))}\2', html, flags=re.DOTALL)

    # 7c. SPOTIFY (Página 10)
    spotify = data.get('SPOTIFY')
    if spotify:
        log("Actualizando SPOTIFY...")
        html = re.sub(r'(<section id="spotify".*?<h2 class="section-title">).*?(</h2>)', rf'\1{html_sanitizer.escape(spotify["kv"].get("TÍTULO", ""))}\2', html, flags=re.DOTALL)
        html = re.sub(r'(<section id="spotify".*?<p class="section-sub[^>]*>).*?(</p>)', rf'\1{html_sanitizer.escape(spotify["kv"].get("SUBTÍTULO", ""))}\2', html, flags=re.DOTALL)
        
        s_list = spotify['lists'].get('PROGRAMAS', [])
        s_cards = re.findall(r'<a[^>]*class="spotify-card[^>]*>.*?</a>', html, flags=re.DOTALL)
        for i, s_name in enumerate(s_list[:4]):
            if i < len(s_cards):
                clean_name = html_sanitizer.escape(re.sub(r'^\d+\.\s*', '', s_name).strip())
                new_card = re.sub(r'alt="[^"]*"', f'alt="{clean_name}"', s_cards[i])
                html = html.replace(s_cards[i], new_card)

    # 8. EQUIPO
    team = data.get('EQUIPO')
    if team:
        log("Actualizando EQUIPO...")
        t_list = team['lists'].get('INTEGRANTES', [])
        t_cards = re.findall(r'<div class="team-card[^>]*>.*?</div>', html, flags=re.DOTALL)
        for i, t_text in enumerate(t_list[:4]):
            if i < len(t_cards):
                parts = t_text.split(':', 1)
                if len(parts) == 2:
                    name = html_sanitizer.escape(re.sub(r'^\d+\.\s*', '', parts[0].strip()))
                    role = html_sanitizer.escape(parts[1].strip())
                    new_card = t_cards[i]
                    new_card = re.sub(r'<h3>.*?</h3>', f'<h3>{name}</h3>', new_card)
                    new_card = re.sub(r'<p>.*?</p>', f'<p>{role}</p>', new_card)
                    html = html.replace(t_cards[i], new_card)

    # 9. CONTACTO
    contact = data.get('CONTACTO')
    if contact:
        log("Actualizando CONTACTO...")
        html = re.sub(r'(<div class="cta-area-full[^>]*>\s*<h2>).*?(</h2>)', rf'\1\n        {html_sanitizer.escape(contact["kv"].get("CTA", ""))}\n      \2', html, flags=re.DOTALL)
        html = re.sub(r'(<div class="cta-area-full[^>]*>.*?<p>).*?(</p>)', rf'\1\n        {html_sanitizer.escape(contact["kv"].get("SUB-CTA", ""))}\n      \2', html, flags=re.DOTALL)
        
        # Datos específicos en footer
        c_list = contact['lists'].get('DATOS DE CONTACTO', [])
        for c_item in c_list:
            if 'WhatsApp' in c_item:
                val = html_sanitizer.escape(c_item.split(':', 1)[1].strip())
                html = re.sub(r'(<li[^>]*whatsapp.*?<span>).*?(</span>)', rf'\1{val}\2', html, flags=re.DOTALL)
            if 'Email' in c_item:
                val = html_sanitizer.escape(c_item.split(':', 1)[1].strip())
                html = re.sub(r'(<li[^>]*gmail.*?<span>).*?(</span>)', rf'\1{val}\2', html, flags=re.DOTALL)
            if 'Dirección' in c_item:
                val = html_sanitizer.escape(c_item.split(':', 1)[1].strip())
                # Split for <br>
                val_html = val.replace(', Providencia', '<br>Providencia')
                html = re.sub(r'(<li[^>]*maplibre.*?<span>).*?(</span>)', rf'\1{val_html}\2', html, flags=re.DOTALL)

    return html

def main():
    log("Iniciando sincronización...")
    
    if not os.path.exists(TXT_FILE):
        log(f"ERROR: No se encontró {TXT_FILE}")
        return
        
    try:
        data = parse_txt()
        log(f"Parseo exitoso. Secciones encontradas: {', '.join(data.keys())}")
        
        html_old = read_file(HTML_FILE)
        
        # Backup
        write_file(BACKUP_FILE, html_old)
        log("Backup creado.")
        
        html_new = update_html(html_old, data)
        
        if html_old != html_new:
            write_file(HTML_FILE, html_new)
            log("¡Sincronización completada con éxito!")
        else:
            log("No se detectaron cambios necesarios.")
            
    except Exception as e:
        log(f"ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
