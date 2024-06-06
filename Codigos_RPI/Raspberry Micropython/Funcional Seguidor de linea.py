from machine import Pin, PWM, UART
import utime

# Configurar la conexión UART (TX: Pin 0, RX: Pin 1)
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Configurar los pines de los motores con PWM para control de velocidad
Motor_A_Adelante = PWM(Pin(18))
Motor_A_Adelante.freq(1000)
Motor_A_Adelante.duty_u16(0)                                                                                                                                                                                                                   


Motor_A_Atras = PWM(Pin(19))
Motor_A_Atras.freq(1000)
Motor_A_Atras.duty_u16(0)

Motor_B_Adelante = PWM(Pin(20))
Motor_B_Adelante.freq(10000)
Motor_B_Adelante.duty_u16(0)

Motor_B_Atras = PWM(Pin(21))
Motor_B_Atras.freq(10000)
Motor_B_Atras.duty_u16(0)

# Configurar el pin 16 como salida
led = Pin("LED", Pin.OUT)

buffer = ""  # Inicializar el buffer vacío
direccion_anterior = None  # Variable para almacenar la dirección anterior

def interpretar_direccion(renglon):
    global direccion_anterior
    
    if all(c == '1' for c in renglon):
        if direccion_anterior == 'izquierda':
            return 'derecha'  # Si es todo unos y la dirección anterior era izquierda, girar a la derecha
        elif direccion_anterior == 'derecha':
        
            return 'izquierda'  # Si es todo unos y la dirección anterior era derecha, girar a la izquierda

        elif direccion_anterior == 'adelante':
        
            return 'atras'  # Si es todo unos y la dirección anterior era derecha, girar a la izquierda

    # Verificar si hay ceros y unos intercalados
    
    # Contar los ceros y unos en el renglón
    num_ceros = renglon.count('0')
    num_unos = renglon.count('1')

    # Si hay más ceros que unos, tomar la dirección como "adelante"
    if num_ceros > num_unos:
        return 'adelante'

    # Verificar si el renglón consiste en todos unos
    
    # Verificar el primer y último carácter del renglón
    primer_caracter = renglon[0]
    ultimo_caracter = renglon[-1]

    # Determinar la dirección basándose en los ceros en el borde
    if primer_caracter == '0':
        direccion = 'izquierda'  # Girar a la derecha si hay un cero al inicio
    elif ultimo_caracter == '0':
        direccion = 'derecha'  # Girar a la izquierda si hay un cero al final
    else:
        direccion = 'adelante'  # Avanzar si no hay ceros en el borde

    # Actualizar la dirección anterior
    direccion_anterior = direccion

    return direccion

# Función para controlar los motores según la dirección
def controlar_motores(direccion):
    if direccion == 'detener':
        Motor_A_Adelante.duty_u16(0)
        Motor_A_Atras.duty_u16(0)
        Motor_B_Adelante.duty_u16(0)
        Motor_B_Atras.duty_u16(0)
    elif direccion == 'adelante':
        Motor_A_Adelante.duty_u16(65000)  # 50% del ciclo de trabajo (mitad de la velocidad)
        Motor_A_Atras.duty_u16(0)
        Motor_B_Adelante.duty_u16(65000)
        Motor_B_Atras.duty_u16(0)
    elif direccion == 'derecha':
        Motor_A_Adelante.duty_u16(65000)
        Motor_A_Atras.duty_u16(0)
        Motor_B_Adelante.duty_u16(0)
        Motor_B_Atras.duty_u16(0)
    elif direccion == 'izquierda':
        Motor_A_Adelante.duty_u16(0)
        Motor_A_Atras.duty_u16(0)
        Motor_B_Adelante.duty_u16(65000)
    elif direccion == 'atras':
        Motor_A_Adelante.duty_u16(0)  # 50% del ciclo de trabajo (mitad de la velocidad)
        Motor_A_Atras.duty_u16(65000)
        Motor_B_Adelante.duty_u16(0)
        Motor_B_Atras.duty_u16(65000)
        Motor_B_Atras.duty_u16(0)

while True:
    try:
        if uart.any():
            datos_recibidos = uart.read(40)  # Leer hasta 40 caracteres
            if datos_recibidos:
                try:
                    texto = datos_recibidos.decode('utf-8').strip()
                    buffer = texto

                    # Imprimir el renglón recibido
                    print("Renglón recibido:", buffer)

                    # Interpretar la dirección
                    direccion = interpretar_direccion(buffer)
                    print("Dirección tomada:", direccion)

                    # Controlar los motores
                    controlar_motores(direccion)

                    # Encender el LED al recibir datos
                    led.toggle()
                except UnicodeError:
                    print("Error al decodificar datos recibidos")
                    direccion = 'detener'
                    controlar_motores(direccion)

                    
    except KeyboardInterrupt:
        break

# Detener todos los motores al salir
Motor_A_Adelante.duty_u16(0)
Motor_A_Atras.duty_u16(0)
Motor_B_Adelante.duty_u16(0)
Motor_B_Atras.duty_u16(0)

# Cerrar la conexión UART al salir
uart.deinit()