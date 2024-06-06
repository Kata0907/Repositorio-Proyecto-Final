import sys
import time
import digitalio
import busio
import board
from adafruit_ov7670 import (
    OV7670,
    OV7670_SIZE_DIV16,
    OV7670_COLOR_YUV,
)

# Configurar el UART
uart = busio.UART(board.GP16, board.GP17, baudrate=115200)

# Configurar el LED incorporado
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Función para enviar texto a través de UART
def enviar_texto(texto):
    uart.write(texto.encode('utf-8'))

# Configuración de la cámara OV7670
cam_bus = busio.I2C(board.GP21, board.GP20)

cam = OV7670(
    cam_bus,
    data_pins=[
        board.GP0,
        board.GP1,
        board.GP2,
        board.GP3,
        board.GP4,
        board.GP5,
        board.GP6,
        board.GP7,
    ],
    clock=board.GP8,
    vsync=board.GP13,
    href=board.GP12,
    mclk=board.GP9,
    shutdown=board.GP15,
    reset=board.GP14,
)
cam.size = OV7670_SIZE_DIV16
cam.colorspace = OV7670_COLOR_YUV
cam.flip_y = True

print(cam.width, cam.height)

# Capturar la primera imagen para inicializar la cámara
first_image = bytearray(2 * cam.width * cam.height)
cam.capture(first_image)
print("Primera imagen capturada")

# Buffer para capturar la imagen
buf = bytearray(2 * cam.width * cam.height)

width = cam.width
height = cam.height

while True:
    # Capturar la imagen actual
    cam.capture(buf)

    # Inicializar una cadena vacía para representar la línea binarizada
    binary_line = ""

    # Iterar sobre los píxeles en la última línea
    for i in range(cam.width):
        intensity = buf[2 * (width * (height - 1) + i)]

        # Si la intensidad es menor o igual a 100, considerar el píxel como negro (0),
        # de lo contrario, considerarlo como blanco (1)
        pixel_value = 0 if intensity <= 100 else 1

        # Agregar el valor del píxel binarizado a la cadena
        binary_line += str(pixel_value)
        
    print(binary_line)

    # Opcional: enviar la línea binarizada a través de UART
    enviar_texto(binary_line)

    # Dormir por un breve periodo de tiempo para reducir la velocidad del bucle si es necesario
    time.sleep(0.1)
