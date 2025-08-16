from machine import Pin, PWM
import time
import urequests

# Configuración de pines
VENTANA_IN1 = Pin(12, Pin.OUT, value=0)  # D6 - Dirección ventana (IN1)
VENTANA_IN2 = Pin(13, Pin.OUT, value=0)  # D7 - Dirección ventana (IN2)
ENABLE_PWM = PWM(Pin(15), freq=1000)  # D8 - PWM motor ventana (EN)
SERVER_URL = "http://192.168.136.88/telegram/comando.txt"

# Variables de estado
DUTY_CYCLE = 500  # PWM
ventanas_abiertas = False  # Estado de las ventanas (False = cerradas, True = abiertas)
cierre_manual = False  # False = No cerrado manualmente, True = Cerrado manualmente

def inicializar_pines():
    """Inicializa los pines apagados."""
    VENTANA_IN1.off()
    VENTANA_IN2.off()
    ENABLE_PWM.duty(0)

def set_motor_speed(duty):
    """Ajusta la velocidad del motor de la ventana con PWM."""
    ENABLE_PWM.duty(duty)

def cerrar_ventanas():
    """Cierra las ventanas con un duty fijo."""
    global ventanas_abiertas
    print("Ventanas CERRÁNDOSE...")    
    VENTANA_IN2.on()     
    VENTANA_IN1.off()
    
    set_motor_speed(DUTY_CYCLE)  # Usa la variable global para la velocidad
    
    time.sleep(6)  # Tiempo estimado para cierre completo
    detener_motores()
    ventanas_abiertas = False  # Actualiza el estado de las ventanas
    print("Ventanas CERRADAS.")
    
    return 0  # Estado de ventanas cerradas

def abrir_ventanas():
    """Abre las ventanas con un duty fijo."""
    global ventanas_abiertas
    print("Ventanas ABRIÉNDOSE...")   
    VENTANA_IN2.off()    
    VENTANA_IN1.on()
    
    set_motor_speed(DUTY_CYCLE)  # Usa la variable global para la velocidad
    
    time.sleep(7)  # Tiempo estimado para apertura completa
    detener_motores()
    ventanas_abiertas = True  # Actualiza el estado de las ventanas
    print("Ventanas ABIERTAS.")
    
    return 1  # Estado de ventanas abiertas

def detener_motores():
    """Detiene los motores apagando los pines de control y el PWM."""
    VENTANA_IN1.off()
    VENTANA_IN2.off()
    set_motor_speed(0)

def leer_comando():
    """Lee el comando desde el servidor XAMPP."""
    try:
        response = urequests.get(SERVER_URL)
        comando = response.text.strip().lower()
        response.close()
        if comando:  # Si hay un comando recibido
            # Reiniciar el archivo con un espacio en blanco
            urequests.get(SERVER_URL.replace("comando.txt", "borrar_comando.php"))
        return comando
    except:
        print("Error al leer comando.")
        return ""

def controlar_por_comando():
    """Ejecuta comandos manuales de apertura, cierre o reseteo de control automático."""
    global ventanas_abiertas, cierre_manual

    comando = leer_comando()

    if comando == "abrir":
        if not ventanas_abiertas:
            cierre_manual = False  # Desactiva el cierre manual si el usuario decide abrir
            return abrir_ventanas()
        else:
            print("Las ventanas ya están abiertas.")
            return 1  # Ya estaban abiertas
    
    elif comando == "cerrar":
        if ventanas_abiertas:
            cierre_manual = True  # Se activa la protección de cierre manual
            return cerrar_ventanas()
        else:
            print("Las ventanas ya están cerradas.")
            return 0  # Ya estaban cerradas

    elif comando == "reset":
        cierre_manual = False  # Reactiva el control automático
        print("Control automático de ventanas restaurado.")
    
    return None  # No se recibió un comando válido

def ejecutar_control_ventanas(temperatura):
    """
    Controla las ventanas basado en temperatura:
    - Se abren si la temperatura supera los 15°C y **NO fueron cerradas manualmente**.
    - Se cierran si la temperatura baja de 10°C.
    """
    global ventanas_abiertas, cierre_manual

    if temperatura < 15:
        if ventanas_abiertas:  # Solo cerrar si estaban abiertas
            cierre_manual = False  # Si el sistema las cierra, permite reabrirlas en el futuro
            return cerrar_ventanas()
        else:
            print("Las ventanas ya están cerradas.")
    
    elif temperatura > 20 and not cierre_manual:  # Solo abrir si NO se cerraron manualmente
        if not ventanas_abiertas:  # Solo abrir si estaban cerradas
            return abrir_ventanas()
        else:
            print("Las ventanas ya están abiertas.")

    return 1 if ventanas_abiertas else 0  # Devuelve el estado actual de las ventanas




# Inicializar pines al importar el módulo
inicializar_pines()



