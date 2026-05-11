import os
import json
import base64
import time
import requests
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest
)

# Configuración desde GitHub Secrets
PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID")
WEBHOOK_URL = os.environ.get("GOOGLE_CHAT_WEBHOOK_URL")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
CREDENTIALS_BASE64 = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
TOKEN_BASE64 = os.environ.get("GOOGLE_TOKEN_BASE64") # Contenido de token.json

HISTORY_FILE = "analytics_tools/notified_history.json"

def get_analytics_client():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    
    # PRIORIDAD 1: Token de Usuario (Bypass para cuentas de empresa/Workspace)
    if TOKEN_BASE64:
        try:
            print("🔍 Detectado GOOGLE_TOKEN_BASE64. Intentando autenticación por Token de Usuario...")
            token_data = json.loads(base64.b64decode(TOKEN_BASE64).decode('utf-8'))
            creds = Credentials.from_authorized_user_info(token_data)
            
            if creds and creds.expired and creds.refresh_token:
                print("🔄 El token ha expirado, intentando refrescar...")
                creds.refresh(Request())
                print("✅ Token refrescado exitosamente.")
            
            client = BetaAnalyticsDataClient(credentials=creds)
            print("🚀 Cliente de Analytics inicializado con Token de Usuario.")
            return client
        except Exception as e:
            print(f"⚠️ Error intentando usar el Token de Usuario: {e}")
            print("Intentando métodos alternativos...")
    
    # PRIORIDAD 2: Credenciales de Cuenta de Servicio (Base64)
    if CREDENTIALS_BASE64:
        try:
            print("🔍 Detectado GOOGLE_CREDENTIALS_BASE64. Intentando autenticación por Cuenta de Servicio...")
            creds_content = base64.b64decode(CREDENTIALS_BASE64).decode('utf-8')
            with open("temp_creds.json", "w") as f:
                f.write(creds_content)
            
            client = BetaAnalyticsDataClient.from_service_account_json("temp_creds.json")
            if os.path.exists("temp_creds.json"):
                os.remove("temp_creds.json")
            print("🚀 Cliente de Analytics inicializado con Cuenta de Servicio (Base64).")
            return client
        except Exception as e:
            if os.path.exists("temp_creds.json"):
                os.remove("temp_creds.json")
            print(f"⚠️ Error intentando usar Cuenta de Servicio (Base64): {e}")

    # PRIORIDAD 3: Credenciales de Cuenta de Servicio (JSON plano)
    if CREDENTIALS_JSON:
        try:
            print("🔍 Detectado GOOGLE_CREDENTIALS_JSON. Intentando autenticación...")
            with open("temp_creds.json", "w") as f:
                f.write(CREDENTIALS_JSON)
            
            client = BetaAnalyticsDataClient.from_service_account_json("temp_creds.json")
            if os.path.exists("temp_creds.json"):
                os.remove("temp_creds.json")
            print("🚀 Cliente de Analytics inicializado con Cuenta de Servicio (JSON plano).")
            return client
        except Exception as e:
            if os.path.exists("temp_creds.json"):
                os.remove("temp_creds.json")
            print(f"⚠️ Error intentando usar Cuenta de Servicio (JSON): {e}")
    
    raise Exception("❌ No se pudo inicializar ninguna forma de autenticación. Verifica los Secretos de GitHub.")


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def send_to_google_chat(webhook_url, message):
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error enviando a Google Chat: {e}")

def monitor():
    if not PROPERTY_ID or not WEBHOOK_URL:
        print("Faltan variables de entorno GA4_PROPERTY_ID o GOOGLE_CHAT_WEBHOOK_URL")
        return

    client = get_analytics_client()
    history = load_history()
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
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
        print("Consultando Google Analytics...")
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
                
                entry_id = f"{date_val}_{hour_val}_{brand}_{model}_{city}_{os_name}".lower().replace(" ", "")
                
                if entry_id not in history:
                    device_info = "💻 Computadora" if cat.lower() == "desktop" else f"📱 {brand} {model}"
                    fmt_date = f"{date_val[6:8]}/{date_val[4:6]} a las {hour_val}:00"
                    
                    msg = (
                        f"✅ *NUEVA VISITA (GITHUB)*\n\n"
                        f"👤 *Dispositivo:* {device_info}\n"
                        f"💻 *Sistema:* {os_name}\n"
                        f"🌐 *Navegador:* {browser}\n"
                        f"📍 *Ubicación:* {city}, {country}\n"
                        f"📅 *Fecha:* {fmt_date}\n"
                        f"------------------------------------------"
                    )
                    
                    send_to_google_chat(WEBHOOK_URL, msg)
                    history.append(entry_id)
                    new_entries += 1
            
            if new_entries > 0:
                save_history(history[-500:])
                print(f"Éxito: {new_entries} nuevas alertas.")
            else:
                print("No hay visitas nuevas.")
        else:
            print("Sin datos de Google todavía.")

    except Exception as e:
        print(f"Error en el monitor: {e}")

if __name__ == "__main__":
    monitor()
