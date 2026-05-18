# Configuración de Google Analytics MCP (Manual)

Para que yo pueda conectarme a tus datos, necesito que sigas estos **3 pasos rápidos**:

### 1. Crear Credenciales en Google Cloud
1.  Ve a [Google Cloud Console](https://console.cloud.google.com/).
2.  Crea un nuevo proyecto llamado `Talentopolis-Analytics`.
3.  Busca **"Google Analytics Data API"** y haz clic en **Habilitar**.
4.  Ve a **IAM y administración > Cuentas de servicio**.
5.  Crea una cuenta, dale un nombre y en el paso de "Claves", selecciona **Agregar clave > Crear clave nueva > JSON**.
6.  Se descargará un archivo. **Cámbiale el nombre a `credentials.json`** y guárdalo en esta misma carpeta (`analytics_tools/`).

### 2. Dar acceso a la cuenta en Analytics
1.  Abre el archivo `credentials.json` y copia el valor de `"client_email"`.
2.  Ve a tu panel de [Google Analytics](https://analytics.google.com/).
3.  Ve a **Administrar > Configuración de la propiedad > Gestión de accesos a la propiedad**.
4.  Haz clic en el botón azul **(+)** y añade el email que copiaste con el rol de **Lector**.

### 3. Obtener tu Property ID
1.  En la configuración de la propiedad en Analytics, busca **"Detalles de la propiedad"**.
2.  Copia el **ID de la propiedad** (un número largo).
3.  Crea un archivo llamado `.env` en esta carpeta y pon:
    `GA4_PROPERTY_ID=TU_ID_AQUI`

---
**Una vez que hagas esto, avísame y podré ejecutar el script para mostrarte tus estadísticas directamente aquí.**
