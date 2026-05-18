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
    raise FileNotFoundError("No se encontro token.json")

def run_country_report(property_id):
    client = get_client()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="country"),
            Dimension(name="city")
        ],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    )
    
    response = client.run_report(request)
    print("\nVISITAS POR PAIS Y CIUDAD (Ultimos 30 dias):")
    print("-" * 60)
    
    total_users = 0
    for row in response.rows:
        country = row.dimension_values[0].value
        city = row.dimension_values[1].value
        users = row.metric_values[0].value
        print(f"{users} usuarios de: {city}, {country}")
        total_users += int(users)
    
    print("-" * 60)
    print(f"TOTAL USUARIOS: {total_users}")
    print("-" * 60)

if __name__ == "__main__":
    prop_id = "537026670"
    run_country_report(prop_id)
