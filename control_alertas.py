import urequests
import time
from machine import Pin, I2C
from ads1x15 import ADS1115

#Conexión con ip estática 
SERVER_URL = "http://192.168.136.88/telegram/telegram.php"

#Inicializar ADS1115
i2c = I2C(scl=Pin(5), sda=Pin(4))  # Pines GPIO5 (D1) y GPIO4 (D2) en ESP8266
ads = ADS1115(i2c)  # Dirección I2C del ADS1115

nivel_min = 2000       # Nivel cuando el tanque está vacío (ADC más bajo)
nivel_max = 9000    # Nivel cuando el tanque está lleno (ADC más alto)

# FUNCIÓN PARA CODIFICAR URL MANUALMENTE EN MICROPYTHON
def urlencode(message):
    return message.replace(" ", "%20").replace("!", "%21").replace("#", "%23") \
                  .replace("$", "%24").replace("&", "%26").replace("'", "%27") \
                  .replace("(", "%28").replace(")", "%29").replace("*", "%2A") \
                  .replace("+", "%2B").replace(",", "%2C").replace("/", "%2F") \
                  .replace(":", "%3A").replace(";", "%3B").replace("=", "%3D") \
                  .replace("?", "%3F").replace("@", "%40").replace("[", "%5B") \
                  .replace("]", "%5D")

# FUNCIÓN PARA ENVIAR ALERTAS A TELEGRAM
def send_to_telegram(message):
    try:
        encoded_message = urlencode(message)
        url = f"{SERVER_URL}?mensaje={encoded_message}"
        print("Enviando alerta a Telegram:", url)
        response = urequests.get(url)
        print("Mensaje enviado.")
        response.close()
    except Exception as e:
        print("Error al enviar mensaje:", str(e))

# FUNCIÓN PARA LEER PROMEDIO DE MÚLTIPLES MUESTRAS DEL SENSOR
def leer_promedio_sensor(num_muestras=10, delay=0.1):
    suma = 0
    for _ in range(num_muestras):
        lectura = ads.read(channel1=2)  # Lee el canal A2 del ADS1115
        suma += lectura
        time.sleep(delay)  # Pequeña pausa entre lecturas
    promedio = suma / num_muestras
    return promedio

# FUNCIÓN PARA LEER EL SENSOR Y VERIFICAR EL NIVEL DEL TANQUE
def verificar_nivel_tanque():
    nivel_raw = leer_promedio_sensor(num_muestras=10, delay=0.1)
    # Convertir a porcentaje de nivel de tanque
    nivel_porcentaje = (nivel_raw - nivel_min) / (nivel_max - nivel_min) * 100
    nivel_porcentaje = max(0, min(100, nivel_porcentaje))  # Limitar entre 0% y 100%

    print(f"Nivel del tanque: {nivel_porcentaje:.1f}% (ADC: {nivel_raw})")

    # Evitar enviar spam de alertas
    if nivel_porcentaje <= 10:  # Consideramos vacío si está por debajo del 10%
        print("¡Tanque vacío! Enviando alerta...")
        send_to_telegram(f"ALERTA: ¡El tanque está vacío! ({nivel_porcentaje:.1f}%) ")
    return nivel_porcentaje

def ejecutar_control_alertas():
        verificar_nivel_tanque()

