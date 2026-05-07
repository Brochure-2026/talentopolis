#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINCRONIZADOR: Textos TXT -> HTML para Talentópolis
Actualiza automáticamente el archivo HTML con los textos del TXT
"""

import re
import os
from pathlib import Path

# Configuración
WORKSPACE = r"c:\Users\Lobitoxic\OneDrive\Documentos\LINEGRAVITY\TALENTOPOLIS"
TXT_FILE = os.path.join(WORKSPACE, "textos_talentopolis.txt")
HTML_FILE = os.path.join(WORKSPACE, "index.html")
BACKUP_FILE = os.path.join(WORKSPACE, "index_backup.html")

def read_txt_file():
    """Lee el archivo TXT y extrae los textos organizados"""
    with open(TXT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def parse_textos(content):
    """Extrae los textos del formato del TXT"""
    textos = {}
    
    # Dividir por secciones
    secciones = re.split(r'### SECCIÓN \d+:', content)
    
    for seccion in secciones[1:]:  # Saltar la primera división (encabezado)
        lineas = seccion.strip().split('\n')
        seccion_nombre = lineas[0].strip()
        
        textos[seccion_nombre] = {}
        
        current_key = None
        current_value = []
        
        for linea in lineas[1:]:
            linea = linea.strip()
            
            if linea.startswith('---') or linea == '':
                continue
                
            if ':' in linea and not linea.startswith('  '):
                # Nueva clave
                if current_key:
                    textos[seccion_nombre][current_key] = '\n'.join(current_value).strip()
                key, value = linea.split(':', 1)
                current_key = key.strip()
                current_value = [value.strip()]
            elif current_key:
                current_value.append(linea)
        
        # Guardar la última clave
        if current_key:
            textos[seccion_nombre][current_key] = '\n'.join(current_value).strip()
    
    return textos


def parse_block_text(value):
    """Convierte un bloque de texto con claves en un diccionario."""
    result = {}
    current_key = None
    current_value = []

    for line in value.splitlines():
        line = line.rstrip()
        if ':' in line and not line.startswith('  '):
            if current_key:
                result[current_key] = '\n'.join(current_value).strip()
            key, val = line.split(':', 1)
            current_key = key.strip()
            current_value = [val.strip()]
        elif current_key:
            current_value.append(line.strip())

    if current_key:
        result[current_key] = '\n'.join(current_value).strip()

    return result


def update_html(html_content, textos):
    """Actualiza el HTML con los textos del TXT"""
    updated_html = html_content
    
    # SECCIÓN 1: HERO
    hero = textos.get('HERO (Portada Principal)', {})
    if hero:
        updated_html = re.sub(
            r'<p class="hero-tagline"[^>]*>.*?</p>',
            f'<p class="hero-tagline" style="text-transform: uppercase; letter-spacing: 2px; color: var(--orange); font-weight: 600; font-size: 0.95rem; margin-bottom: 12px;">\n      {hero.get("TAGLINE", "")}\n    </p>',
            updated_html,
            flags=re.DOTALL
        )
        
        updated_html = re.sub(
            r'<h1 class="text-center"[^>]*>.*?</h1>',
            f'<h1 class="text-center" style="max-width: 100%; margin: 0 auto 20px auto; font-size: 3.2rem; line-height: 1.1; font-weight: 900; color: var(--white);">\n      {hero.get("HEADLINE", "")}\n    </h1>',
            updated_html,
            flags=re.DOTALL
        )
        
        updated_html = re.sub(
            r'<p class="hero-sub"[^>]*>.*?</p>',
            f'<p class="hero-sub" style="max-width: 750px; font-size: 1.2rem; line-height: 1.5; color: rgba(255,255,255,0.7); margin: 0 auto;">\n      {hero.get("DESCRIPCIÓN", "")}\n    </p>',
            updated_html,
            flags=re.DOTALL
        )
    
    # SECCIÓN 2: ABOUT
    about = textos.get('ABOUT (Quiénes Somos)', {})
    if about:
        # Título de sección
        pattern_label = r'(<p class="section-label" style="color: var\(--orange\);">).*?(</p>)'
        updated_html = re.sub(pattern_label, f'\\1{about.get("LABEL", "")}\\2', updated_html, count=1)
        
        # Intentar actualizar el primer título de ABOUT
        pattern_title = r'(<h2 class="section-title">).*?(</h2>)'
        matches = list(re.finditer(pattern_title, updated_html))
        if matches and len(matches) > 0:
            first_match = matches[0]
            title_text = f'El punto de encuentro entre la <span style="color: var(--orange);">mirada editorial</span> y la capacidad técnica'
            updated_html = updated_html[:first_match.start()] + f'<h2 class="section-title">{title_text}</h2>' + updated_html[first_match.end():]

    # SECCIÓN 7: COMUNICARTE
    comunicarte = textos.get('COMUNICARTE (Formato Destacado)', {})
    if comunicarte:
        section_match = re.search(r'(<section[^>]*id="comunicarte"[^>]*>)(.*?)(</section>)', updated_html, flags=re.DOTALL)
        if section_match:
            section_start, section_content, section_end = section_match.group(1), section_match.group(2), section_match.group(3)

            section_content = re.sub(
                r'(<p class="section-label" style="color:var\(--orange\); margin-bottom: 5px;">).*?(</p>)',
                f'\\1{comunicarte.get("LABEL", "")}\\2',
                section_content,
                count=1,
                flags=re.DOTALL
            )
            section_content = re.sub(
                r'(<h2[^>]*>).*?(</h2>)',
                f'\\1{comunicarte.get("TÍTULO", "")}\\2',
                section_content,
                count=1,
                flags=re.DOTALL
            )
            section_content = re.sub(
                r'(<p class="section-sub"[^>]*>).*?(</p>)',
                f'\\1{comunicarte.get("DESCRIPCIÓN", "")}\\2',
                section_content,
                count=1,
                flags=re.DOTALL
            )

            guest_keys = ['INVITADO 1', 'INVITADO 2', 'INVITADO 3']
            guest_index = 0

            def replace_guest(match):
                nonlocal guest_index
                guest_html = match.group(0)
                if guest_index >= len(guest_keys):
                    guest_index += 1
                    return guest_html

                guest_data = parse_block_text(comunicarte.get(guest_keys[guest_index], ''))
                guest_index += 1

                if not guest_data:
                    return guest_html

                name = guest_data.get('Nombre', '')
                especialidad = guest_data.get('Especialidad', '').replace('\n', '<br>')
                descripcion = guest_data.get('Descripción', '')

                guest_html = re.sub(r'<h4>.*?</h4>', f'<h4>{name}</h4>', guest_html, flags=re.DOTALL)
                guest_html = re.sub(r'<span>.*?</span>', f'<span>{especialidad}</span>', guest_html, flags=re.DOTALL)
                guest_html = re.sub(r'<p>.*?</p>', f'<p>{descripcion}</p>', guest_html, flags=re.DOTALL, count=1)
                return guest_html

            section_content = re.sub(
                r'<div class="guest-card">.*?<div class="guest-info">.*?</div>\s*</div>',
                replace_guest,
                section_content,
                flags=re.DOTALL
            )

            updated_html = updated_html[:section_match.start(2)] + section_content + updated_html[section_match.end(2):]

    print("✅ HTML actualizado exitosamente")
    return updated_html

def save_backup(html_content):
    """Crea una copia de seguridad del HTML original"""
    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"💾 Backup creado: {BACKUP_FILE}")

def save_updated_html(html_content):
    """Guarda el HTML actualizado"""
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ HTML guardado: {HTML_FILE}")

def main():
    print("=" * 80)
    print("SINCRONIZADOR TALENTÓPOLIS - TXT to HTML")
    print("=" * 80)
    
    try:
        # Verificar archivos
        if not os.path.exists(TXT_FILE):
            print(f"❌ Error: No se encontró {TXT_FILE}")
            return False
        
        if not os.path.exists(HTML_FILE):
            print(f"❌ Error: No se encontró {HTML_FILE}")
            return False
        
        print(f"📄 Leyendo TXT: {TXT_FILE}")
        txt_content = read_txt_file()
        
        print("🔍 Parsing textos...")
        textos = parse_textos(txt_content)
        
        print("📋 Secciones encontradas:")
        for seccion in textos.keys():
            print(f"  • {seccion}")
        
        print(f"\n📖 Leyendo HTML: {HTML_FILE}")
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("💾 Creando backup...")
        save_backup(html_content)
        
        print("🔄 Actualizando HTML con textos del TXT...")
        updated_html = update_html(html_content, textos)
        
        print("💿 Guardando HTML actualizado...")
        save_updated_html(updated_html)
        
        print("\n" + "=" * 80)
        print("✅ SINCRONIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print("\n💡 Próximos pasos:")
        print("   1. Edita los textos en: textos_talentopolis.txt")
        print("   2. Ejecuta este script nuevamente")
        print("   3. El HTML se actualizará automáticamente")
        print(f"\n📝 Backup disponible en: {BACKUP_FILE}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
