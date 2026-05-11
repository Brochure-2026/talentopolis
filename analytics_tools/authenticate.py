import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes para leer datos de Analytics
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

def main():
    creds = None
    token_path = os.path.join('analytics_tools', 'token.json')
    client_secrets_path = os.path.join('analytics_tools', 'client_secrets.json')

    if not os.path.exists(client_secrets_path):
        print(f"ERROR: No se encuentra {client_secrets_path}")
        return

    # El flujo de OAuth2
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
    
    print("\n" + "="*50)
    print("INICIANDO AUTENTICACION OAUTH2")
    print("="*50)
    print("Se abrira una ventana en tu navegador.")
    print("Si no se abre, copia el link que aparezca abajo.")
    print("="*50 + "\n")

    # Ejecutar el servidor local para capturar el token
    creds = flow.run_local_server(port=0, prompt='consent')

    # Guardar las credenciales para la próxima vez
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    
    print("\n" + "="*50)
    print("¡AUTENTICACION EXITOSA!")
    print(f"Token guardado en: {token_path}")
    print("="*50)

if __name__ == '__main__':
    main()
