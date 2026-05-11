import os
import json
import base64
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest
)

def get_analytics_client():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    
    # 1. Intentar con GOOGLE_TOKEN_BASE64 (Entorno GitHub/Cloud)
    token_base64 = os.environ.get("GOOGLE_TOKEN_BASE64")
    if token_base64:
        print("🔍 Usando GOOGLE_TOKEN_BASE64...")
        token_data = json.loads(base64.b64decode(token_base64).decode('utf-8'))
        creds = Credentials.from_authorized_user_info(token_data)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return BetaAnalyticsDataClient(credentials=creds)

    # 2. Intentar con token.json (Local)
    token_path = "analytics_tools/token.json"
    if os.path.exists(token_path):
        print("🔍 Usando token.json local...")
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/analytics.readonly'])
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return BetaAnalyticsDataClient(credentials=creds)
    
    # 3. Intentar con GOOGLE_CREDENTIALS_BASE64
    creds_base64 = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
    if creds_base64:
        print("🔍 Usando GOOGLE_CREDENTIALS_BASE64...")
        creds_content = base64.b64decode(creds_base64).decode('utf-8')
        with open("temp_gen_creds.json", "w") as f:
            f.write(creds_content)
        client = BetaAnalyticsDataClient.from_service_account_json("temp_gen_creds.json")
        os.remove("temp_gen_creds.json")
        return client

    # 4. Intentar con credentials.json (Local Service Account)
    creds_path = "analytics_tools/credentials.json"
    if os.path.exists(creds_path):
        print("🔍 Usando credentials.json local...")
        return BetaAnalyticsDataClient.from_service_account_json(creds_path)
    
    raise Exception("❌ No se encontró ninguna credencial válida (token.json, credentials.json o variables Base64)")

def generate_report():
    # Obtener PROPERTY_ID de .env o variables de entorno
    property_id = None
    if os.path.exists("analytics_tools/.env"):
        with open("analytics_tools/.env", "r") as f:
            for line in f:
                if line.startswith("GA4_PROPERTY_ID="):
                    property_id = line.split("=")[1].strip()
    
    if not property_id:
        # Intentar obtener de las variables de entorno de la sesión si existen
        property_id = os.environ.get("GA4_PROPERTY_ID")
    
    if not property_id:
        print("Error: No se encontró GA4_PROPERTY_ID en .env")
        return

    client = get_analytics_client()
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
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
        date_ranges=[DateRange(start_date="90daysAgo", end_date="today")],
    )

    try:
        response = client.run_report(request)
        
        report_md = "# 📊 Reporte Histórico de Dispositivos (Últimos 30 días)\n\n"
        report_md += "| Fecha/Hora | Dispositivo | Sistema | Navegador | Ubicación | Usuarios |\n"
        report_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        if not response.rows:
            report_md += "| - | No hay datos disponibles | - | - | - | - |\n"
        else:
            # Ordenar por fecha y hora descendente
            rows = sorted(response.rows, key=lambda x: (x.dimension_values[0].value, x.dimension_values[1].value), reverse=True)
            
            for row in rows:
                date_val = row.dimension_values[0].value
                hour_val = row.dimension_values[1].value
                cat = row.dimension_values[2].value
                brand = row.dimension_values[3].value
                model = row.dimension_values[4].value
                os_name = row.dimension_values[5].value
                browser = row.dimension_values[6].value
                city = row.dimension_values[7].value
                country = row.dimension_values[8].value
                users = row.metric_values[0].value
                
                fmt_date = f"{date_val[6:8]}/{date_val[4:6]} {hour_val}:00"
                device = "💻 Computadora" if cat.lower() == "desktop" else f"📱 {brand} {model}"
                location = f"{city}, {country}"
                
                report_md += f"| {fmt_date} | {device} | {os_name} | {browser} | {location} | {users} |\n"
        
        with open("analytics_tools/last_full_report.md", "w", encoding="utf-8") as f:
            f.write(report_md)
            
        print("Reporte generado exitosamente en analytics_tools/last_full_report.md")
        
    except Exception as e:
        print(f"Error generando reporte: {e}")

if __name__ == "__main__":
    generate_report()
