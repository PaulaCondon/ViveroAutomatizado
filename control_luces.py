from machine import Pin, I2C, RTC
from ads1x15 import ADS1115
import time

# Configuración de I2C y sensor ADS1115
i2c = I2C(scl=Pin(5), sda=Pin(4))

# Inicializa el ADS1115 en la dirección I2C 0x48 (por defecto)
ads = ADS1115(i2c)

# Configuración del LED
led = Pin(2, Pin.OUT)

# Configuración del RTC para obtener la hora
rtc = RTC()

def obtener_hora():
    """Devuelve la hora actual."""
    return rtc.datetime()[4]  # (YYYY, MM, DD, W, HH, MM, SS, MS)

def es_horario_restringido():
    """Verifica si estamos entre las 23:00 y 5:00 (donde la luz debe estar apagada)."""
    hora = obtener_hora()
    return 23 <= hora or hora < 5  # Apaga entre las 23 y las 5

def leer_promedio_adc(canal=0, num_muestras=10, retardo=0.1):
    """Lee el valor ADC varias veces y devuelve el promedio para una mayor estabilidad."""
    suma = 0
    for i in range(num_muestras):
        try:
            lectura = ads.read(channel1=canal)
        except Exception as e:
            print(f"Error al leer el canal {canal}: {e}")
            lectura = 0
        suma += lectura
        time.sleep(retardo)
    return suma / num_muestras

def obtener_luminosidad():
    """Obtiene la luminosidad medida por el sensor ADS1115."""
    return leer_promedio_adc(canal=0, num_muestras=10, retardo=0.1)

def controlar_luz():
    """Controla la luz según la luminosidad promediada y el horario."""
    if es_horario_restringido():
        led.value(1)  # Apagar luz
        print("Luz apagada por horario (23:00 - 05:00)")
        time.sleep(1)
        return

    # Obtener el promedio de lecturas de luminosidad
    luz_promedio = leer_promedio_adc(canal=0, num_muestras=10, retardo=0.1)
    print(f"Luminosidad medida: {luz_promedio}")
    time.sleep(1)

    if luz_promedio < 1000:
        led.value(0)  # ENCENDER luz (LED activo bajo)
        print("Luz ENCENDIDA")
    else:
        led.value(1)  # APAGAR luz
        print("Luz APAGADA")

def ejecutar_control_luces():
        """Ejecuta control de la iluminación."""
        controlar_luz() 
