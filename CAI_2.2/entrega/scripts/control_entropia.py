import os
import numpy as np
from collections import Counter

def entropia_shannon(data):
    conteo = Counter(data)
    n = len(data)
    probs = np.array([c/n for c in conteo.values()])
    return -np.sum(probs * np.log2(probs))

# Control: datos verdaderamente aleatorios del mismo tamano
aleatorio = os.urandom(3_000_000)
print("Control (os.urandom, deberia dar ~8.0):", round(entropia_shannon(aleatorio), 4))

# Ahora miramos bloques repetidos de 16 bytes en Firma1Cifrada (indicio de modo ECB)
with open("Firma1Cifrada.bmp", "rb") as f:
    data = f.read()

bloques = [data[i:i+16] for i in range(0, len(data)-15, 16)]
contador_bloques = Counter(bloques)
repetidos = {b: c for b, c in contador_bloques.items() if c > 1}
print(f"\nTotal bloques de 16 bytes: {len(bloques)}")
print(f"Bloques distintos: {len(contador_bloques)}")
print(f"Bloques que se repiten (>1 vez): {len(repetidos)}")
if repetidos:
    top = sorted(repetidos.items(), key=lambda x: -x[1])[:5]
    for b, c in top:
        print(f"  Bloque {b.hex()} se repite {c} veces")

# Entropia por "ventanas": comparamos entropia de los primeros 100KB vs ultimos 100KB
print("\nEntropia primeros 100KB:", round(entropia_shannon(data[:100_000]), 4))
print("Entropia ultimos 100KB:", round(entropia_shannon(data[-100_000:]), 4))
print("Entropia bytes 1.000.000-1.100.000:", round(entropia_shannon(data[1_000_000:1_100_000]), 4))
