import numpy as np
from PIL import Image

PATH = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_2.2\Dibujo.bmp"
img = np.array(Image.open(PATH).convert("RGB"))
h, w, _ = img.shape
lsb = img & 1
bit1 = (img >> 1) & 1

coincidencia = np.array([(lsb[y] == bit1[y]).mean() for y in range(h)])
desvio = np.abs(coincidencia - 0.5)

# Suavizamos con media movil de 5 filas para evitar falsos positivos aislados
k = 5
suavizado = np.convolve(desvio, np.ones(k)/k, mode='same')

print("Filas 270-338 (donde se ve el cambio):")
for y in range(270, h):
    marca = "  <-- estructurado" if suavizado[y] > 0.12 else ""
    print(f"{y:4d} | coincidencia={coincidencia[y]*100:5.1f}%  desvio_suavizado={suavizado[y]*100:5.1f}%{marca}")

# Transicion real: ultima fila (de arriba a abajo) donde sigue siendo ruido antes de
# entrar en zona sostenida estructurada (varias filas seguidas con desvio alto)
umbral = 0.12
ventana_confirmacion = 5
primera_estructurada = None
for y in range(h - ventana_confirmacion):
    if np.all(suavizado[y:y+ventana_confirmacion] > umbral):
        primera_estructurada = y
        break

if primera_estructurada:
    bits_mensaje = primera_estructurada * w * 3
    print(f"\n>>> Transicion sostenida en fila {primera_estructurada} de {h}")
    print(f">>> Bytes estimados ocupados por el mensaje: ~{bits_mensaje/8:.0f} bytes")
