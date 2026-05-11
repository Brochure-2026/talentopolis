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
    """Obtiene el cliente de Analytics usando Token (OAuth2) o Credentials (Service Account)."""
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    service_account_path = os.path.join(os.path.dirname(__file__), 'credentials.json')

    # 1. Intentar con Token OAuth2 (Plan B)
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/analytics.readonly'])
        # Refrescar si ha expirado
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return BetaAnalyticsDataClient(credentials=creds)

    # 2. Fallback a Service Account (Plan A)
    if os.path.exists(service_account_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
        return BetaAnalyticsDataClient()

    raise FileNotFoundError("No se encontró ni token.json ni credentials.json en la carpeta analytics_tools.")

def run_sample_report(property_id):
    """Ejecuta un reporte básico de usuarios y sesiones."""
    client = get_client()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    )
    
    try:
        response = client.run_report(request)
        print("\n--- REPORTE DE GOOGLE ANALYTICS (GA4) ---")
        print("Usuarios Activos por Ciudad (Ultimos 7 dias):")
        print("-" * 40)
        
        if not response.rows:
            print("No hay datos suficientes todavia.")
        else:
            for row in response.rows:
                print(f"{row.dimension_values[0].value}: {row.metric_values[0].value} usuarios")
        print("-" * 40)
    except Exception as e:
        print(f"ERROR en la API de Analytics: {e}")

if __name__ == "__main__":
    # Obtener Property ID
    prop_id = os.getenv("GA4_PROPERTY_ID")
    
    # Si no esta en el entorno, intentar leer de .env manualmente
    if not prop_id:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith("GA4_PROPERTY_ID="):
                        prop_id = line.split("=")[1].strip()

    if not prop_id:
        print("ERROR: No se encontro GA4_PROPERTY_ID en el entorno ni en el archivo .env.")
    else:
        run_sample_report(prop_id)
