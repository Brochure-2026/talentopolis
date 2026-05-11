import os
import json
import time
import requests
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest
)
from google.cloud import storage
from google.oauth2 import service_account

# Configuración desde variables de entorno (Set in Google Cloud Console)
PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID")
WEBHOOK_URL = os.environ.get("GOOGLE_CHAT_WEBHOOK_URL")
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME") # Cubo para guardar el historial
HISTORY_FILE = "notified_history.json"

def get_analytics_client():
    # En Google Cloud Functions, si usamos la cuenta de servicio por defecto o adjunta,
    # no necesitamos el archivo JSON explícitamente si tiene los permisos.
    # Pero para asegurar compatibilidad con lo que ya tiene el usuario:
    if os.path.exists("credentials.json"):
        return BetaAnalyticsDataClient.from_service_account_json("credentials.json")
    return BetaAnalyticsDataClient()

def load_history_from_gcs():
    if not BUCKET_NAME:
        return []
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(HISTORY_FILE)
        if blob.exists():
            data = blob.download_as_text()
            return json.loads(data)
    except Exception as e:
        print(f"Error cargando historial de GCS: {e}")
    return []

def save_history_to_gcs(history):
    if not BUCKET_NAME:
        return
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(HISTORY_FILE)
        blob.upload_from_string(json.dumps(history))
    except Exception as e:
        print(f"Error guardando historial en GCS: {e}")

def send_to_google_chat(webhook_url, message):
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error enviando a Google Chat: {e}")

def monitor_handler(event, context):
    """Entry point para Google Cloud Function (Cloud Scheduler trigger)"""
    if not PROPERTY_ID or not WEBHOOK_URL:
        return "Falta configuración de variables de entorno", 500

    client = get_analytics_client()
    history = load_history_from_gcs()
    
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
                        f"✅ *NUEVA VISITA (CLOUD)*\n\n"
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
                save_history_to_gcs(history[-500:])
                return f"Monitor completado. {new_entries} nuevas alertas.", 200
        
        return "No hay nuevas visitas.", 200

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}", 500

# Para pruebas locales
if __name__ == "__main__":
    # Simular una ejecución local si se desea
    print("Para ejecutar localmente usa detailed_monitor.py")
