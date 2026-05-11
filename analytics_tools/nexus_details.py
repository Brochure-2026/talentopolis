import os
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, FilterExpression, Filter
)
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Forzar salida en UTF-8
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
    raise Exception("Token no encontrado.")

def run_nexus_report(property_id):
    client = get_client()

    # Dimensiones extra pedidas: Ciudad, SO, Navegador
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="mobileDeviceModel"),
            Dimension(name="city"),
            Dimension(name="operatingSystem"),
            Dimension(name="browser"),
            Dimension(name="country")
        ],
        metrics=[Metric(name="activeUsers")],
        # Filtrar solo por el Nexus 5X
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="mobileDeviceModel",
                string_filter=Filter.StringFilter(value="Nexus 5X")
            )
        ),
        date_ranges=[DateRange(start_date="2020-01-01", end_date="today")],
    )
    
    try:
        response = client.run_report(request)
        print("\n" + "="*50)
        print("DETALLES DEL USUARIO NEXUS 5X")
        print("="*50)
        
        if not response.rows:
            print("No se encontraron detalles adicionales para este dispositivo.")
        else:
            for row in response.rows:
                print(f"📍 UBICACION: {row.dimension_values[1].value}, {row.dimension_values[4].value}")
                print(f"💻 SISTEMA: {row.dimension_values[2].value}")
                print(f"🌐 NAVEGADOR: {row.dimension_values[3].value}")
                print(f"👥 USUARIOS: {row.metric_values[0].value}")
                print("-" * 30)
        print("="*50 + "\n")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Obtener Property ID
    prop_id = None
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("GA4_PROPERTY_ID="):
                    prop_id = line.split("=")[1].strip()

    if not prop_id:
        print("ERROR: No se encontro GA4_PROPERTY_ID.")
    else:
        run_nexus_report(prop_id)
