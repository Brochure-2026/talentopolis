# Guía de Despliegue a la Nube (Google Cloud)

Para que el monitor de TALENTOPOLIS corra de forma independiente sin necesidad de tu computadora, seguiremos estos pasos para subirlo a **Google Cloud Functions**.

### Paso 1: Preparar los archivos
Ya he preparado una carpeta llamada `deploy_cloud` en tu proyecto con todo lo necesario:
- `main.py`: El código optimizado para la nube.
- `requirements.txt`: Las librerías que necesita Google.
- `credentials.json`: Tu acceso a Analytics (copia de seguridad).

### Paso 2: Crear un "Cubo" de Almacenamiento (Cloud Storage)
Como la nube "olvida" lo que hizo cada vez que termina, necesitamos un lugar donde guardar la memoria (quién ya fue notificado).
1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Busca **Cloud Storage** > **Buckets**.
3. Haz clic en **CREATE**.
4. Nombre: Ponle algo como `talentopolis-monitor-memoria` (anota este nombre).
5. Dale a **CREATE** (puedes dejar todo lo demás por defecto).

### Paso 3: Crear la Función (Cloud Function)
1. Busca **Cloud Functions** en la consola de Google.
2. Haz clic en **CREATE FUNCTION**.
3. **Configuración Básica**:
   - Environment: **2nd gen**.
   - Function name: `monitor-analytics`.
   - Region: `us-central1` (o la que prefieras).
   - Trigger: **HTTPS**.
   - (Importante) Marca "Allow unauthenticated invocations" para probarla al principio.
4. **Runtime, Build, Connections... (Variables de Entorno)**:
   - Despliega esta sección y ve a **Runtime environment variables**.
   - Agrega estas 3 variables:
     1. `GA4_PROPERTY_ID`: (Tu ID de propiedad de Analytics)
     2. `GOOGLE_CHAT_WEBHOOK_URL`: (Tu link de Google Chat)
     3. `GCS_BUCKET_NAME`: (El nombre del cubo que creaste en el Paso 2)
5. Haz clic en **NEXT**.

### Paso 4: Subir el Código
1. En **Runtime**, selecciona **Python 3.10** (o superior).
2. En **Entry point**, escribe: `monitor_handler`.
3. Tienes dos opciones:
   - **Opción A**: Selecciona "ZIP Upload" y sube el contenido de la carpeta `deploy_cloud` (debes comprimir los 3 archivos juntos en un .zip).
   - **Opción B**: Copia y pega el contenido de `main.py` y `requirements.txt` directamente en el editor de la consola.
4. Haz clic en **DEPLOY**.

### Paso 5: Automatizar (Cloud Scheduler)
Para que revise cada 30 minutos automáticamente:
1. Busca **Cloud Scheduler**.
2. Haz clic en **CREATE JOB**.
3. Nombre: `ejecutar-monitor-cada-30m`.
4. Frequency: `*/30 * * * *` (Esto significa cada 30 minutos).
5. Target Type: **HTTP**.
6. URL: Pega la URL que te dio la Cloud Function al terminar el Paso 4.
7. HTTP Method: **POST**.
8. Haz clic en **CREATE**.

¡Listo! Con esto, Google revisará Analytics cada 30 minutos y te mandará el mensaje a Chat si hay alguien nuevo, sin que tengas que hacer nada en tu PC o celular.
