import machine
import dht
import time
import control_ventanas 

# Configurar el pin donde está conectado el DHT11
dht_pin = machine.Pin(0)  # D3 (GPIO0)
sensor = dht.DHT11(dht_pin)

# Configurar el pin del ventilador (D0 - GPIO16)
ventilador = machine.Pin(16, machine.Pin.OUT)
ventilador.value(0)  # Apagar ventilador al inicio

# Umbrales para activar el ventilador
TEMP_UMBRAL = 15  # Temperatura en °C
HUM_UMBRAL = 60   # Humedad en %

def obtener_temperatura():
    """Obtiene la temperatura desde el sensor DHT11."""
    try:
        sensor.measure()  # Nueva lectura
        return sensor.temperature()
    except OSError as e:
        print(f"Error al leer la temperatura: {e}")
        return None  # Devolver None en caso de error

def obtener_humedad_aire():
    """Obtiene la humedad del aire desde el sensor DHT11."""
    try:
        sensor.measure()  # Nueva lectura
        return sensor.humidity()
    except OSError as e:
        print(f"Error al leer la humedad: {e}")
        return None  # Devolver None en caso de error

def obtener_estado_ventilador():
    """Devuelve el estado del ventilador (1=encendido, 0=apagado)."""
    return ventilador.value()

def controlar_temperatura():
    """Lee la temperatura y humedad, y controla el ventilador según los umbrales."""
    try:
        temp = obtener_temperatura()
        hum = obtener_humedad_aire()
        
        if control_ventanas.ventanas_abiertas:
            ventilador.value(0)
            print("Ventanas abiertas. Ventilador APAGADO.")
            return

        if temp is not None and hum is not None:  # Solo continuar si las lecturas son válidas
            print(f"Temperatura: {temp:.1f}°C")
            print(f"Humedad: {hum:.1f}%")

            # Verificar si la temperatura o la humedad superan los umbrales
            if temp > TEMP_UMBRAL or hum >= HUM_UMBRAL:
                ventilador.value(1)  # Encender ventilador
                print("Temperatura alta o humedad elevada. Ventilador ENCENDIDO.")
            else:
                ventilador.value(0)  # Apagar ventilador
                print("Temperatura y humedad normales. Ventilador apagado.")
        else:
            print("Error en la lectura del sensor DHT11. No se controlará el ventilador.")

    except OSError as e:
        print(f"Error en el control de temperatura: {e}")

def ejecutar_control_temperatura():
    """Ejecuta la medición de temperatura y controla el ventilador una sola vez."""
    controlar_temperatura()
