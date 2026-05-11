import os
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Forzar salida en UTF-8 para evitar errores en terminales Windows
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def get_client():
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/analytics.readonly'])
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return BetaAnalyticsDataClient(credentials=creds)
    raise FileNotFoundError("No se encontro token.json. Ejecuta authenticate.py primero.")

def run_device_report(property_id):
    client = get_client()

    # Dimensiones completas para el listado historico
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
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    )
    
    try:
        response = client.run_report(request)
        print("\n" + "╔" + "═"*115 + "╗")
        print("║" + " LISTADO DETALLADO POR HORA (Últimos 30 días) ".center(115) + "║")
        print("╠" + "═"*115 + "╣")
        
        header = f"{'FECHA/HORA':<15} | {'DISPOSITIVO':<30} | {'SISTEMA':<15} | {'UBICACIÓN':<25} | {'USR':<5}"
        print(f"║ {header} ║")
        print("╟" + "─"*115 + "╢")
        
        if not response.rows:
            print("║" + " No se encontraron datos históricos recientes. ".center(115) + "║")
        else:
            # Ordenar por fecha y hora (mas recientes primero)
            rows = sorted(response.rows, key=lambda x: (x.dimension_values[0].value, x.dimension_values[1].value), reverse=True)
            
            for row in rows:
                date_val = row.dimension_values[0].value  # YYYYMMDD
                hour_val = row.dimension_values[1].value  # HH
                cat = row.dimension_values[2].value
                brand = row.dimension_values[3].value
                model = row.dimension_values[4].value
                os_name = row.dimension_values[5].value
                browser = row.dimension_values[6].value
                city = row.dimension_values[7].value
                country = row.dimension_values[8].value
                users = row.metric_values[0].value
                
                # Formatear fecha/hora
                fmt_date = f"{date_val[6:8]}/{date_val[4:6]} {hour_val}:00"
                
                # Formatear el nombre del dispositivo
                if cat.lower() == "desktop":
                    device_info = "💻 Computadora"
                else:
                    device_info = f"📱 {brand} {model}"
                
                location = f"{city}, {country}"
                
                line = f"{fmt_date:<15} | {device_info[:29]:<30} | {os_name[:14]:<15} | {location[:24]:<25} | {users:<5}"
                print(f"║ {line} ║")
                
        print("╚" + "═"*115 + "╝\n")
        print("⚠️  Nota: Los datos históricos de Google pueden tardar hasta 24-48h en procesarse completamente.")
        print("   Para ver quién está conectado justo ahora, usa runner.py.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    prop_id = os.getenv("GA4_PROPERTY_ID")
    if not prop_id:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith("GA4_PROPERTY_ID="):
                        prop_id = line.split("=")[1].strip()

    if not prop_id:
        print("ERROR: No se encontro GA4_PROPERTY_ID.")
    else:
        run_device_report(prop_id)
