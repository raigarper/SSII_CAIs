import numpy as np
from PIL import Image

PATH = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_2.2\Dibujo.bmp"
img = np.array(Image.open(PATH).convert("RGB"))
h, w, _ = img.shape

lsb = img & 1  # bit menos significativo de cada canal, por fila

# Para cada fila, miramos si el patron de LSB "se parece" al patron del
# bit inmediatamente superior (bit 1), que es una buena aproximacion de
# "estructura natural de la imagen". Si los LSB fueron sobreescritos con
# un mensaje, dejan de parecerse a bit1 y se vuelven ~50% aleatorios.
bit1 = (img >> 1) & 1

coincidencia_por_fila = []
for y in range(h):
    igual = (lsb[y] == bit1[y]).mean()  # proporcion de bits iguales entre LSB y bit1
    coincidencia_por_fila.append(igual)

coincidencia_por_fila = np.array(coincidencia_por_fila)

print("Fila | % coincidencia LSB vs bit1 (bajo=ruido/mensaje, alto=estructura original)")
for y in range(0, h, 20):
    print(f"{y:4d} | {coincidencia_por_fila[y]*100:.1f}%")

# Buscamos la fila donde cambia de "ruido" (~50%) a "estructura" (bien por encima/debajo de 50%)
# Umbral simple: diferencia respecto al 50% ideal de un bit aleatorio
desvio = np.abs(coincidencia_por_fila - 0.5)
# encontramos la primera fila, empezando por abajo, donde el desvio supera un umbral claro
umbral = 0.08
filas_estructuradas = np.where(desvio > umbral)[0]
if len(filas_estructuradas) > 0:
    primera_fila_estructurada = filas_estructuradas[0]
    print(f"\nTransicion estimada ruido->estructura en la fila: {primera_fila_estructurada} de {h}")
    bits_hasta_ahi = primera_fila_estructurada * w * 3
    bytes_hasta_ahi = bits_hasta_ahi / 8
    print(f"Eso equivale a ~{bytes_hasta_ahi:.0f} bytes desde el inicio de la imagen")
    print(f"(Para comparar: VSL dijo que el mensaje declarado media 37099 bytes,")
    print(f" y LSB-RS estimo 27299 bytes -> el rango es compatible)")
else:
    print("No se detecto una transicion clara")
