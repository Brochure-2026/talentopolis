import os
import json
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient

# Forzar salida en UTF-8 para evitar errores en terminales Windows
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def diagnostic():
    creds_path = os.path.join("analytics_tools", "credentials.json")
    if not os.path.exists(creds_path):
        print(f"Error: No se encuentra {creds_path}")
        return

    with open(creds_path, 'r') as f:
        data = json.load(f)
        email = data.get("client_email")
        print(f"--- DIAGNOSTICO DE ANALYTICS ---")
        print(f"1. Email de la cuenta de servicio: {email}")
        print(f"   ESTE ES EL EMAIL QUE DEBES ANADIR EN GOOGLE ANALYTICS.")
        print(f"2. Property ID configurado: {os.getenv('GA4_PROPERTY_ID')}")
        print(f"---------------------------------")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    client = BetaAnalyticsDataClient()
    
    try:
        print("Probando conexion...")
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
        request = RunReportRequest(
            property=f"properties/{os.getenv('GA4_PROPERTY_ID')}",
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="yesterday", end_date="today")],
        )
        client.run_report(request)
        print("CONEXION EXITOSA! Ya tienes acceso.")
    except Exception as e:
        print(f"ERROR DE PERMISOS: {e}")
        print("\nINSTRUCCIONES PARA SOLUCIONAR:")
        print(f"1. Entra a https://analytics.google.com/")
        print("2. Ve a Administrar (icono de engranaje abajo a la izquierda).")
        print(f"3. En la columna de 'Propiedad' (la del medio), busca 'Gestion de accesos a la propiedad'.")
        print(f"4. Haz clic en el boton azul (+) -> 'Anadir usuarios'.")
        print(f"5. Pega EXACTAMENTE este email: {email}")
        print("6. Asegurate de que el rol sea 'Lector' (Viewer).")
        print("7. Desmarca la casilla 'Notificar a los nuevos usuarios por correo electronico'.")
        print("8. Haz clic en 'Anadir'.")

if __name__ == "__main__":
    diagnostic()
