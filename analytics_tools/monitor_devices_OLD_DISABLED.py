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

KNOWN_DEVICES_FILE = os.path.join(os.path.dirname(__file__), 'known_devices.json')

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

# Memoria temporal para no repetir notificaciones (se limpia al reiniciar el script)
# Formato: {"ciudad_pais_dispositivo": timestamp}
NOTIFIED_USERS = {}
COOLDOWN_SECONDS = 1800  # 30 minutos de espera para volver a avisar de la misma persona

def monitor():
    config = get_config()
    prop_id = config.get("GA4_PROPERTY_ID")
    webhook_url = config.get("GOOGLE_CHAT_WEBHOOK_URL")

    if not prop_id or not webhook_url: 
        print("Falta configuracion en .env (GA4_PROPERTY_ID o GOOGLE_CHAT_WEBHOOK_URL)")
        return

    client = get_analytics_client()
    
    from google.analytics.data_v1beta.types import RunRealtimeReportRequest
    
    request = RunRealtimeReportRequest(
        property=f"properties/{prop_id}",
        dimensions=[
            Dimension(name="deviceCategory"),
            Dimension(name="city"),
            Dimension(name="country"),
            Dimension(name="platform")
        ],
        metrics=[Metric(name="activeUsers")],
    )

    try:
        current_time = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Revisando actividad...")
        response = client.run_realtime_report(request)
        
        if response.rows:
            active_count = 0
            for row in response.rows:
                cat = row.dimension_values[0].value
                city = row.dimension_values[1].value or "Desconocida"
                country = row.dimension_values[2].value or "Desconocido"
                platform = row.dimension_values[3].value or "Web"
                
                # Crear un identificador unico para esta persona/ubicacion
                user_id = f"{city}_{country}_{cat}_{platform}".lower().replace(" ", "")
                
                # Verificar si ya avisamos de esta persona recientemente
                last_notified = NOTIFIED_USERS.get(user_id, 0)
                if current_time - last_notified > COOLDOWN_SECONDS:
                    msg = f"🚀 *NUEVA VISITA DETECTADA*\n\n"
                    msg += f"📱 *Tipo:* {cat.capitalize()} ({platform})\n"
                    msg += f"📍 *Ubicacion:* {city}, {country}\n"
                    msg += f"⏰ *Hora:* {time.strftime('%H:%M:%S')}"
                    send_to_google_chat(webhook_url, msg)
                    NOTIFIED_USERS[user_id] = current_time
                    active_count += 1
            
            if active_count > 0:
                print(f"Notificaciones enviadas para {active_count} nuevo(s) usuario(s).")
            else:
                print("Los usuarios detectados ya fueron notificados recientemente.")
        else:
            print("Sin actividad en este momento.")

    except Exception as e:
        print(f"Error en el monitoreo: {e}")

if __name__ == "__main__":
    monitor()
