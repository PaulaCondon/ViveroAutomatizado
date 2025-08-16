import urequests  
import network
import time

THINGSPEAK_WRITE_API_KEY = "E0BAB1CF2L7PABZJ"
THINGSPEAK_URL = "http://api.thingspeak.com/update"

def enviar_datos(humedad_suelo, luminosidad, temperatura, humedad_aire, nivel_tanque, estado_ventanas, estado_ventilador):
    """Envía datos de los sensores a ThingSpeak usando GET."""
    try:
        # Construir la URL con los parámetros correspondientes
        url = (
            f"{THINGSPEAK_URL}?api_key={THINGSPEAK_WRITE_API_KEY}"
            f"&field1={humedad_suelo:.1f}"
            f"&field2={luminosidad:.1f}"
            f"&field3={temperatura}"
            f"&field4={humedad_aire}"
            f"&field5={nivel_tanque:.1f}"
            f"&field6={estado_ventanas}"
            f"&field7={estado_ventilador:}"
        )
        
        print("Enviando datos a ThingSpeak...")
        response = urequests.get(url)
        print(f"Envío de datos relizado.")
        response.close()
        
        time.sleep(1) 
    
    except Exception as e:
        print(f"Error al enviar datos a ThingSpeak: {e}")

def ejecutar_envio_thingspeak(humedad_suelo, luminosidad, temperatura, humedad_aire, nivel_tanque, estado_ventanas, estado_ventilador):
    """Ejecuta el envío de datos a ThingSpeak usando GET."""
    enviar_datos(humedad_suelo, luminosidad, temperatura, humedad_aire, nivel_tanque, estado_ventanas, estado_ventilador)
