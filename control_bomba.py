from machine import Pin, I2C
from ads1x15 import ADS1115
import time

# Configuración del I2C para ADS1115 en ESP8266 (D1=SCL, D2=SDA)
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)  # Configurar frecuencia I2C

# Inicializar ADS1115
ads = ADS1115(i2c)  # Dirección por defecto 0x48

bomba = Pin(14, Pin.OUT, value=0)  # GPIO14 (D5) inicia apagada

HUMEDAD_SECO_ADC = 25000    # Suelo completamente seco (0% humedad)
HUMEDAD_HUMEDO_ADC = 12000   # Suelo completamente mojado (100% humedad)

# Umbrales de control con histéresis
HUMEDAD_ENCENDER = 40  # Si la humedad baja del 40%, encender bomba
HUMEDAD_APAGAR = 60    # Si la humedad sube del 60%, apagar bomba

def obtener_humedad_porcentaje(valor_adc):
    """Convierte el valor ADC en un porcentaje de humedad correctamente."""
    
    if valor_adc >= HUMEDAD_SECO_ADC:  
        return 0.0  # Suelo completamente seco (0% humedad)
    elif valor_adc <= HUMEDAD_HUMEDO_ADC:  
        return 100.0  # Suelo completamente húmedo (100% humedad)
    else:
        humedad = ((HUMEDAD_SECO_ADC - valor_adc) / (HUMEDAD_SECO_ADC - HUMEDAD_HUMEDO_ADC))  * 100
        return round(min(humedad, 100), 1) 

def leer_promedio_adc(canal=1, num_muestras=10, retardo=0.1):
    """Lee el valor ADC varias veces y devuelve el promedio para mayor estabilidad."""
    suma = 0
    for i in range(num_muestras):
        try:
            lectura = ads.read(channel1=canal)
        except Exception as e:
            print(f"Error al leer el canal {canal}: {e}")
            lectura = 0
        suma += lectura
        time.sleep(retardo)
    promedio = suma / num_muestras
    return promedio

def controlar_bomba():
    """Controla la bomba en base a la humedad medida con histéresis."""
    try:
        humedad_adc_promedio = leer_promedio_adc(canal=1, num_muestras=10, retardo=0.1)
        humedad_porcentaje = obtener_humedad_porcentaje(humedad_adc_promedio)

        # Mostrar resultado
        print(f"Humedad del suelo: {humedad_porcentaje:.2f}% (ADC: {humedad_adc_promedio})")

        # Encender la bomba si la humedad baja del 40%
        if humedad_porcentaje < HUMEDAD_ENCENDER :  
            bomba.value(0)  # ENCENDER bomba
            print("Bomba ENCENDIDA")

        # Apagar la bomba si la humedad sube del 60%
        elif humedad_porcentaje > HUMEDAD_APAGAR :
            bomba.value(1)  # APAGAR bomba
            print("Bomba APAGADA")

        # Si está entre 40% y 60%, no hacer nada (histéresis)
        else:
            print("Humedad en zona segura, sin cambios en la bomba")
            bomba.value(1)

    except Exception as e:
        print(f"Error en la lectura: {e}")
        
def obtener_humedad_suelo():
    """Obtiene la humedad del suelo leyendo el sensor y convirtiéndolo a porcentaje."""
    humedad_adc = leer_promedio_adc(canal=1)  # Leer del ADC en el canal 1
    return obtener_humedad_porcentaje(humedad_adc)  # Convertir a porcentaje

def ejecutar_control_bomba():
    """Ejecuta la medición de humedad y controla la bomba una sola vez."""
    controlar_bomba()
