import network
import socket
from time import sleep
import machine
from machine import Pin, PWM

ssid = 'Snow'
password = 'A2720528'

# Configurar PWM para controlar la velocidad de la llanta A y B
pwm_A = PWM(Pin(17))  # Pin GPIO 17 para controlar la velocidad de la llanta A
pwm_A.freq(1000)  # Frecuencia de PWM
pwm_B = PWM(Pin(16))  # Pin GPIO 16 para controlar la velocidad de la llanta B
pwm_B.freq(1000)  # Frecuencia de PWM

velocidad_A = 65535  # Valor de ciclo de trabajo PWM inicial para llanta A (rango: 0-65535)
velocidad_B = 65535  # Valor de ciclo de trabajo PWM inicial para llanta B (rango: 0-65535)
#pwm_A.duty_u16(velocidad_A)  # Establecer el ciclo de trabajo PWM inicial para llanta A
#pwm_B.duty_u16(velocidad_B)  # Establecer el ciclo de trabajo PWM inicial para llanta B

def adelante():
    Motor_A_Adelante.value(1)
    Motor_B_Adelante.value(1)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(0)
    pwm_A.duty_u16(60000)  # Reducir la velocidad de la llanta A cuando se mueve hacia la izquierda
    pwm_B.duty_u16(60000)  # Aumentar la velocidad de la llanta B cuando se mueve hacia la izquierda

def atras():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(1)
    Motor_B_Atras.value(1)
    pwm_A.duty_u16(60000)  # Establecer el ciclo de trabajo PWM inicial para llanta A
    pwm_B.duty_u16(60000)  # Establecer el ciclo de trabajo PWM inicial para llanta B

def detener():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(0)
    pwm_A.duty_u16(0)  # Detener llanta A
    pwm_B.duty_u16(0)  # Detener llanta B

def izquierda():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(1)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(0)
    pwm_A.duty_u16(0)  # Reducir la velocidad de la llanta A cuando se mueve hacia la izquierda
    pwm_B.duty_u16(60000)  # Aumentar la velocidad de la llanta B cuando se mueve hacia la izquierda

def derecha():
    Motor_A_Adelante.value(1)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(0)
    pwm_A.duty_u16(60000)  # Aumentar la velocidad de la llanta A cuando se mueve hacia la derecha
    pwm_B.duty_u16(0)  # Reducir la velocidad de la llanta B cuando se mueve hacia la derecha

detener()
    
def conectar():
    red = network.WLAN(network.STA_IF)
    red.active(True)
    red.connect(ssid, password)
    while red.isconnected() == False:
        print('Conectando ...')
        sleep(1)
    ip = red.ifconfig()[0]
    print(f'Conectado con IP: {ip}')
    return ip
    
def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def pagina_web():
    html = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    button {
                        touch-action: manipulation;
                    }
                </style>
                <script>
                    function enviarComando(comando) {
                        var xhttp = new XMLHttpRequest();
                        xhttp.open("GET", "/" + comando, true);
                        xhttp.send();
                    }

                    function presionado(comando) {
                        enviarComando(comando);
                        setTimeout(function(){ enviarComando('detener'); }, 1000);
                    }
                </script>
            </head>
            <body>
            <center>
            <button id="adelante" ontouchstart="presionado('adelante')">Adelante</button>
            <table><tr>
            <td><button id="izquierda" ontouchstart="presionado('izquierda')">Izquierda</button></td>
            <td><button id="detener" disabled>Detener</button></td>
            <td><button id="derecha" ontouchstart="presionado('derecha')">Derecha</button></td>
            </tr></table>
            <button id="atras" ontouchstart="presionado('atras')">Atras</button>
            </body>
            </html>
            """
    return html

def serve(connection):
    while True:
        cliente = connection.accept()[0]
        peticion = cliente.recv(1024)
        peticion = str(peticion)
        try:
            peticion = peticion.split()[1]
        except IndexError:
            pass
        if peticion == '/adelante':
            adelante()
            sleep(2)
            detener()
        elif peticion == '/izquierda':
            izquierda()
            sleep(2)
            detener()
        elif peticion == '/derecha':
            derecha()
            sleep(2)
            detener()
        elif peticion == '/atras':
            atras()
            sleep(2)
            detener()
        cliente.send(pagina_web())
        cliente.close()

try:
    ip = conectar()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
