import os
import sys
from PIL import Image
import pillow_heif
import rawpy

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

SOURCE_DIR = r"C:\Users\Lobitoxic\OneDrive\Documentos\LINEGRAVITY\TALENTOPOLIS\assets\Fotos_fondo_slides"
TARGET_DIR = r"C:\Users\Lobitoxic\OneDrive\Documentos\LINEGRAVITY\TALENTOPOLIS\assets"

def convert_cr3(src_path, dest_path):
    print(f"[*] Convirtiendo CR3 raw: {os.path.basename(src_path)} -> {os.path.basename(dest_path)}...")
    with rawpy.imread(src_path) as raw:
        # Postprocess raw image to RGB numpy array
        rgb = raw.postprocess(use_camera_wb=True, half_size=True) # half_size to speed up and reduce output resolution appropriately
        img = Image.fromarray(rgb)
        # Resize to max width 1920 to keep it lightweight for web background
        img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        img.save(dest_path, "JPEG", quality=82)
    print(f"[+] Convertido con éxito: {os.path.basename(dest_path)}")

def convert_heic(src_path, dest_path):
    print(f"[*] Convirtiendo HEIC: {os.path.basename(src_path)} -> {os.path.basename(dest_path)}...")
    img = Image.open(src_path)
    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
    img.save(dest_path, "JPEG", quality=82)
    print(f"[+] Convertido con éxito: {os.path.basename(dest_path)}")

def convert_jpg(src_path, dest_path):
    print(f"[*] Comprimiendo JPG pesado: {os.path.basename(src_path)} -> {os.path.basename(dest_path)}...")
    img = Image.open(src_path)
    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
    img.save(dest_path, "JPEG", quality=82)
    print(f"[+] Optimizado con éxito: {os.path.basename(dest_path)}")

def main():
    print("--- INICIANDO CONVERSIÓN Y OPTIMIZACIÓN DE FOTOS ---")
    if not os.path.exists(SOURCE_DIR):
        print(f"ERROR: No existe la carpeta {SOURCE_DIR}")
        return

    files = os.listdir(SOURCE_DIR)
    for filename in files:
        src_path = os.path.join(SOURCE_DIR, filename)
        if os.path.isdir(src_path):
            continue
            
        base_name, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # Mapear nombre destino en la carpeta assets directamente
        dest_filename = f"{base_name}.jpg"
        dest_path = os.path.join(TARGET_DIR, dest_filename)
        
        try:
            if ext == '.cr3':
                convert_cr3(src_path, dest_path)
            elif ext == '.heic':
                convert_heic(src_path, dest_path)
            elif ext in ['.jpg', '.jpeg']:
                convert_jpg(src_path, dest_path)
            else:
                print(f"[!] Archivo omitido (formato no soportado): {filename}")
        except Exception as e:
            print(f"[R] Error procesando {filename}: {str(e)}")
            
    print("--- PROCESO DE IMÁGENES COMPLETADO ---")

if __name__ == "__main__":
    main()
