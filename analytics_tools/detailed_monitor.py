import os
import json
import time
import requests
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest
)
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Forzar salida en UTF-8
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'notified_history.json')

def get_config():
    config = {}
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config

def get_analytics_client():
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/analytics.readonly'])
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return BetaAnalyticsDataClient(credentials=creds)
    raise Exception("Token no encontrado.")

def send_to_google_chat(webhook_url, message):
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error enviando a Google Chat: {e}")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def monitor():
    config = get_config()
    prop_id = config.get("GA4_PROPERTY_ID")
    webhook_url = config.get("GOOGLE_CHAT_WEBHOOK_URL")

    if not prop_id or not webhook_url: 
        print("Falta configuracion en .env")
        return

    client = get_analytics_client()
    history = load_history()
    
    # Pedimos los ultimos 3 dias para asegurar que no se nos escape nada que se haya procesado tarde
    request = RunReportRequest(
        property=f"properties/{prop_id}",
        dimensions=[
            Dimension(name="date"),
            Dimension(name="hour"),
            Dimension(name="deviceCategory"),
            Dimension(name="mobileDeviceBranding"),
            Dimension(name="mobileDeviceModel"),
            Dimension(name="operatingSystem"),
            Dimension(name="browser"),
            Dimension(name="city"),
            Dimension(name="country")
        ],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="2daysAgo", end_date="today")],
    )

    try:
        print(f"[{time.strftime('%H:%M:%S')}] Escaneando base de datos de Google (Modo Alta Precision)...")
        response = client.run_report(request)
        
        new_entries = 0
        if response.rows:
            for row in response.rows:
                date_val = row.dimension_values[0].value
                hour_val = row.dimension_values[1].value
                cat = row.dimension_values[2].value
                brand = row.dimension_values[3].value
                model = row.dimension_values[4].value
                os_name = row.dimension_values[5].value
                browser = row.dimension_values[6].value
                city = row.dimension_values[7].value
                country = row.dimension_values[8].value
                
                # Crear ID unico para esta visita especifica
                entry_id = f"{date_val}_{hour_val}_{brand}_{model}_{city}_{os_name}".lower().replace(" ", "")
                
                if entry_id not in history:
                    # Formatear el nombre del dispositivo
                    if cat.lower() == "desktop":
                        device_info = "💻 Computadora"
                    else:
                        device_info = f"📱 {brand} {model}"
                    
                    fmt_date = f"{date_val[6:8]}/{date_val[4:6]} a las {hour_val}:00"
                    
                    msg = f"✅ *NUEVA VISITA CONFIRMADA (DETALLE TOTAL)*\n\n"
                    msg += f"👤 *Dispositivo:* {device_info}\n"
                    msg += f"💻 *Sistema:* {os_name}\n"
                    msg += f"🌐 *Navegador:* {browser}\n"
                    msg += f"📍 *Ubicacion:* {city}, {country}\n"
                    msg += f"📅 *Fecha:* {fmt_date}\n"
                    msg += f"------------------------------------------"
                    
                    send_to_google_chat(webhook_url, msg)
                    history.append(entry_id)
                    new_entries += 1
            
            save_history(history[-500:]) # Guardamos los ultimos 500 para no inflar el archivo
            if new_entries > 0:
                print(f"Se enviaron {new_entries} nuevas alertas detalladas.")
            else:
                print("No hay visitas nuevas procesadas por Google todavia.")
        else:
            print("Google todavia no tiene datos procesados de este periodo.")

    except Exception as e:
        print(f"Error en el monitoreo detallado: {e}")

if __name__ == "__main__":
    monitor()
