import time
import detailed_monitor as dm

def run_loop():
    print("--- INICIANDO ALARMAS DE ALTA PRECISIÓN ---")
    print("Este modo enviará notificaciones con TODO el detalle (Modelo, Navegador, etc.)")
    print("Nota: Las alertas llegarán cuando Google procese los datos (aprox. 12-24h después).")
    print("Revisando nuevas visitas cada 30 minutos...")
    
    while True:
        try:
            dm.monitor()
        except Exception as e:
            print(f"Error en el ciclo: {e}")
        
        # Esperar 30 minutos entre revisiones (los datos historicos no cambian cada minuto)
        time.sleep(1800) 

if __name__ == "__main__":
    try:
        run_loop()
    except KeyboardInterrupt:
        print("Monitoreo detenido.")
