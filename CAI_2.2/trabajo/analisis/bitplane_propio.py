import numpy as np
from PIL import Image

base = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_2.2\trabajo"
out = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_2.2\trabajo\analisis"
img = np.array(Image.open(base + "\carrier_lsb_larga.bmp").convert("RGB"))
lsb_plane = (img & 1) * 255
Image.fromarray(lsb_plane.astype(np.uint8)).save(out + "\carrier_lsb_larga_bitplane.png")
print("Guardado bit-plane de carrier_lsb_larga.bmp")

bit1 = (img >> 1) & 1
lsb = img & 1
h, w, _ = img.shape
coincidencia = np.array([(lsb[y] == bit1[y]).mean() for y in range(h)])
desvio = np.abs(coincidencia - 0.5)
k = 5
suavizado = np.convolve(desvio, np.ones(k)/k, mode='same')
umbral = 0.12
ventana = 5
transicion = None
for y in range(h - ventana):
    if np.all(suavizado[y:y+ventana] > umbral):
        transicion = y
        break
print(f"Transicion detectada en fila: {transicion} de {h}" if transicion else "Sin transicion clara detectada")
if transicion:
    bytes_estimados = (transicion * w * 3) / 8
    print(f"Bytes estimados: ~{bytes_estimados:.0f}  (mensaje real: 432 caracteres = 432 bytes + cabecera)")
