import os
import json
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient

# Forzar salida en UTF-8 para evitar errores en terminales Windows
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def diagnostic():
    property_id = os.getenv('GA4_PROPERTY_ID')
    token_base64 = os.getenv('GOOGLE_TOKEN_BASE64')
    creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    print(f"--- DIAGNÓSTICO DE ANALYTICS (MODO HÍBRIDO) ---")
    print(f"Propiedad GA4 ID: {property_id}")
    print(f"Token de Usuario (Base64): {'PRESENTE' if token_base64 else 'AUSENTE'}")
    print(f"Cuenta Servicio (Base64): {'PRESENTE' if creds_base64 else 'AUSENTE'}")
    print(f"Cuenta Servicio (JSON): {'PRESENTE' if creds_json else 'AUSENTE'}")
    print(f"----------------------------------------------")

    # Intentar obtener cliente usando la misma lógica que el monitor
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import base64

    client = None
    method_used = "Ninguno"

    # 1. Probar Token
    if token_base64:
        try:
            print("Probando Token de Usuario...")
            token_data = json.loads(base64.b64decode(token_base64).decode('utf-8'))
            creds = Credentials.from_authorized_user_info(token_data)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            client = BetaAnalyticsDataClient(credentials=creds)
            method_used = "Token de Usuario"
        except Exception as e:
            print(f"Error con Token: {e}")

    # 2. Probar Service Account si Token falló o no existe
    if not client and (creds_base64 or creds_json):
        try:
            print("Probando Cuenta de Servicio...")
            content = base64.b64decode(creds_base64).decode('utf-8') if creds_base64 else creds_json
            with open("temp_diagnostic.json", "w") as f:
                f.write(content)
            client = BetaAnalyticsDataClient.from_service_account_json("temp_diagnostic.json")
            method_used = "Cuenta de Servicio"
            if os.path.exists("temp_diagnostic.json"): os.remove("temp_diagnostic.json")
        except Exception as e:
            print(f"Error con Cuenta de Servicio: {e}")
            if os.path.exists("temp_diagnostic.json"): os.remove("temp_diagnostic.json")

    if not client:
        print("❌ ERROR: No se pudo inicializar ningún cliente. Revisa tus credenciales.")
        return

    print(f"✅ Cliente inicializado vía: {method_used}")
    
    try:
        print("Enviando reporte de prueba...")
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
        request = RunReportRequest(
            property=f"properties/{property_id}",
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="yesterday", end_date="today")],
        )
        response = client.run_report(request)
        print(f"✅ ¡CONEXIÓN EXITOSA! Se recibieron {len(response.rows)} filas de datos.")
    except Exception as e:
        print(f"❌ ERROR EN LA LLAMADA A LA API: {e}")
        if "403" in str(e):
            print("\nPOSIBLE SOLUCIÓN:")
            print("Si usas Cuenta de Servicio: Asegúrate de haber añadido el email al acceso de la propiedad.")
            print("Si usas Token: Asegúrate de que tu cuenta personal tenga permisos en la propiedad y que el token sea reciente.")

if __name__ == "__main__":
    diagnostic()
