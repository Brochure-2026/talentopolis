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
    raise FileNotFoundError("No se encontro token.json")

def run_unique_devices(property_id):
    client = get_client()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="deviceCategory"),
            Dimension(name="mobileDeviceBranding"),
            Dimension(name="mobileDeviceModel"),
            Dimension(name="operatingSystem"),
            Dimension(name="browser")
        ],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    )
    
    response = client.run_report(request)
    devices = set()
    
    for row in response.rows:
        cat = row.dimension_values[0].value
        brand = row.dimension_values[1].value
        model = row.dimension_values[2].value
        os_name = row.dimension_values[3].value
        browser = row.dimension_values[4].value
        
        if cat.lower() == "desktop":
            device_str = f"Computadora (Sistema: {os_name}, Navegador: {browser})"
        else:
            device_str = f"{brand} {model} (Sistema: {os_name}, Navegador: {browser})"
        
        devices.add(device_str)
    
    print("\nLISTADO DE DISPOSITIVOS UNICOS (Ultimos 30 dias):")
    print("-" * 60)
    if not devices:
        print("No se detectaron dispositivos todavia.")
    for i, dev in enumerate(sorted(list(devices)), 1):
        print(f"{i}. {dev}")
    print("-" * 60)

if __name__ == "__main__":
    prop_id = "537026670"
    run_unique_devices(prop_id)
