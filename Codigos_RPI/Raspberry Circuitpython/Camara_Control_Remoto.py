import time
import board
import pwmio
import digitalio
import busio
from adafruit_ov7670 import (
    OV7670,
    OV7670_SIZE_DIV16,
    OV7670_COLOR_YUV,
    OV7670_TEST_PATTERN_COLOR_BAR_FADE,
)

# Configurar pines PWM
pwm_pin = board.GP18
led_pwm = pwmio.PWMOut(pwm_pin, frequency=1000, duty_cycle=0)

# Configurar cámara OV7670
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

# Capturar la primera imagen
first_image = bytearray(2 * cam.width * cam.height)
cam.capture(first_image)
print("Primera imagen capturada")

buf = bytearray(2 * cam.width * cam.height)

width = cam.width

# Definir las posiciones de referencia del primer y último cero
ref_first_zero_pos = 5
ref_last_zero_pos = 35

total_error_first = 0
total_error_last = 0
num_lines = 0
direction = None
straight_count = 0  # Contador de desviaciones rectas
diagonal_count = 0  # Contador de desviaciones diagonales

# Definir listas para almacenar las posiciones de ceros
first_zero_positions = []
last_zero_positions = []

while True:
    # Capturar la imagen actual
    cam.capture(buf)

    # Inicializar variables para el cálculo del error promedio
    total_error_first = 0
    total_error_last = 0
    num_lines = 0
    straight_count = 0
    diagonal_count = 0

    # Limpiar listas de posiciones de ceros
    first_zero_positions.clear()
    last_zero_positions.clear()

    # Mostrar solo las líneas del 10 al 20 de la imagen actual
    for j in range(10, 21):
        # Inicializar una cadena vacía para representar la línea binarizada
        binary_line = ""

        # Iterar sobre los píxeles en la línea actual
        for i in range(cam.width):
            intensity = buf[2 * (width * j + i)]

            # Si la intensidad es menor o igual a 100, considerar el píxel como negro (0),
            # de lo contrario, considerarlo como blanco (1)
            pixel_value = 0 if intensity <= 100 else 1

            # Agregar el valor del píxel binarizado a la cadena
            binary_line += str(pixel_value)

        # Encontrar la posición del primer cero
        zero_pos = binary_line.find('0')
        # Encontrar la posición del último cero
        last_zero_pos = binary_line.rfind('0')

        # Actualizar las listas de posiciones de ceros
        first_zero_positions.append(zero_pos)
        last_zero_positions.append(last_zero_pos)

        # Calcular el error porcentual para el primer cero
        if zero_pos == -1:
            percent_error_first = 100
        else:
            percent_error_first = abs((zero_pos - ref_first_zero_pos) * 100 / ref_first_zero_pos)

        # Calcular el error porcentual para el último cero
        if last_zero_pos == -1:
            percent_error_last = 100
        else:
            percent_error_last = abs((last_zero_pos - ref_last_zero_pos) * 100 / ref_last_zero_pos)

        # Si el porcentaje es mayor que 100, ajustarlo a 100
        percent_error_first = min(percent_error_first, 100)
        percent_error_last = min(percent_error_last, 100)

        # Actualizar el total de errores y el número de líneas
        total_error_first += percent_error_first
        total_error_last += percent_error_last
        num_lines += 1

        # Determinar si la desviación es recta
        if percent_error_first == percent_error_last:
            straight_count += 1
        else:
            diagonal_count += 1

        # Imprimir la línea binarizada y el error porcentual
        print(f"Línea {j}: {binary_line}, Error primer cero: {percent_error_first:.2f}%, Error último cero: {percent_error_last:.2f}%")

    # Calcular el error promedio para el primer y último cero
    avg_error_first = total_error_first / num_lines
    avg_error_last = total_error_last / num_lines

    # Determinar si la desviación es recta o diagonal
    if straight_count >= 5 or any(first_zero_positions.count(pos) >= 5 for pos in first_zero_positions):
        # Si más de la mitad de las líneas tienen un patrón consistente o alguna posición de ceros se repite mucho,
        # considerar la desviación como recta
        direction = "recta"
    else:
        direction = "diagonal"

    # Determinar la dirección de la desviación
    if all(pos != -1 for pos in first_zero_positions):
        # Si todas las líneas tienen al menos un cero
        avg_zero_pos = sum(first_zero_positions) / len(first_zero_positions)
        if avg_zero_pos < ref_first_zero_pos:
            deviation_direction = "izquierda"
        elif avg_zero_pos > ref_first_zero_pos:
            deviation_direction = "derecha"
        else:
            deviation_direction = "no se puede determinar"
    else:
        # Si no hay ningún cero en ninguna línea
        deviation_direction = "no se puede determinar"
    
    av=((avg_error_first+avg_error_last)/2)
    # Imprimir las codificaciones
    print(f"1. Error promedio primer cero: {avg_error_first:.2f}%")
    print(f"2. Error promedio último cero: {avg_error_last:.2f}%")
    print(f"3. Tipo de desviación: {direction}")
    print(f"4. Dirección de la desviación: {deviation_direction}")
    print(f"1. Error promedio : {av:.2f}%")

    # Actualizar el ciclo de trabajo del PWM
    led_pwm.duty_cycle = int(((avg_error_first+avg_error_last)/2) / 100 * 65535)  # Usamos el valor correspondiente al error promedio primer cero

    time.sleep(1)

