#-------main.py-------#
import control_luces
import control_bomba
import control_temperatura
import control_ventanas
import control_alertas
import envio_thingspeak
import network
import time
from ntptime import settime
from machine import RTC
    
def conectar_wifi():
    """Conexión del ESP8266 a la red WiFi."""
    ssid = "MiRed"
    password = "12345678"
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect() 
    time.sleep(1)
    
    if not wlan.isconnected():
        print("                 ")
        print("              ***Bienvenidos al jardín del futuro***                    ")
        print("                 ")
        time.sleep(1)
        print(f"Conectando a {ssid}...")
        wlan.connect(ssid, password)
        for i in range(30):  # Espera hasta 30 intentos (~30s)
            if wlan.isconnected():
                print(f"Conectado a {ssid} con IP: {wlan.ifconfig()[0]}")
                return True
            print(f"Esperando conexión...")
            time.sleep(1)
    print("No se pudo conectar a WiFi")
    return False

def sincronizar_hora():
    """Sincroniza la hora con NTP."""
    try:
        settime()
        rtc = RTC()
        # Ajustar la zona horaria
        fecha_hora = list(rtc.datetime())  # Obtener lista de valores de fecha y hora
        fecha_hora[4] = (fecha_hora[4] - 3) % 24  # Ajustar horas asegurando que esté en el rango 0-23
        rtc.datetime(tuple(fecha_hora))  # Aplicar la hora corregida
        print(f"Hora sincronizada con NTP: {rtc.datetime()[4]:02}:{rtc.datetime()[5]:02}")
    except Exception as e:
        print("Error al sincronizar la hora NTP:", e)


def ejecutar():
    """Ejecuta las funciones en orden y envía datos a ThingSpeak."""
    while True:
        # Sincronización y control 
        # Ejecución de controles
        sincronizar_hora()  # Sincronizar horario
        control_luces.ejecutar_control_luces()
        control_bomba.ejecutar_control_bomba()
        control_temperatura.ejecutar_control_temperatura()

        # Obtener datos de sensores
        nivel_tanque = control_alertas.verificar_nivel_tanque()
        humedad_suelo = control_bomba.obtener_humedad_suelo()
        luminosidad = control_luces.obtener_luminosidad()
        temperatura = control_temperatura.obtener_temperatura()
        humedad_aire = control_temperatura.obtener_humedad_aire()
        
        comando = control_ventanas.controlar_por_comando()

        # Control de ventanas y ventilador
        estado_ventanas = control_ventanas.ejecutar_control_ventanas(temperatura)
        estado_ventilador = control_temperatura.obtener_estado_ventilador()

        # Envío de datos a ThingSpeak
        envio_thingspeak.ejecutar_envio_thingspeak(
            humedad_suelo, luminosidad, temperatura, humedad_aire,
            nivel_tanque, estado_ventanas, estado_ventilador
        )

        
        time.sleep(1)

# Conectar a WiFi antes de iniciar el control
if conectar_wifi():
    ejecutar() 
else:
    print("No se intentará sincronizar la hora porque no hay conexión WiFi")  
