import numpy as np
from PIL import Image
import hashlib

with open("Firma1Cifrada.bmp", "rb") as f:
    data = f.read()

# La imagen original (Firma2/Firma3) es 1280x800, 24 bits -> 3840 bytes/fila (divisible entre 16: 240 bloques/fila)
W_BLOQUES = 240
H = 800
N_BLOQUES_PIXELES = W_BLOQUES * H  # 192000

# Probamos varios offsets de inicio (por la cabecera BMP + padding de cifrado),
# ya que no sabemos el tamaño exacto de cabecera tras cifrar.
mejor = None
for offset_bytes in range(0, 64, 16):
    bloques = [data[i:i+16] for i in range(offset_bytes, offset_bytes + N_BLOQUES_PIXELES*16, 16)]
    if len(bloques) < N_BLOQUES_PIXELES:
        continue
    # mapeamos cada bloque unico a un tono de gris (hash estable del bloque)
    unicos = {}
    grises = np.zeros(N_BLOQUES_PIXELES, dtype=np.uint8)
    for idx, b in enumerate(bloques):
        if b not in unicos:
            h = hashlib.md5(b).digest()[0]
            unicos[b] = h
        grises[idx] = unicos[b]
    img = grises.reshape(H, W_BLOQUES)
    out = Image.fromarray(img, 'L').resize((W_BLOQUES*4, H*4), Image.NEAREST)
    out.save(f"revelado_offset_{offset_bytes}.png")
    print(f"offset {offset_bytes}: {len(unicos)} bloques unicos en esta zona, guardado revelado_offset_{offset_bytes}.png")
