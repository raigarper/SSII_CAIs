import numpy as np
from collections import Counter

def entropia_shannon(path):
    with open(path, 'rb') as f:
        data = f.read()
    conteo = Counter(data)
    n = len(data)
    probs = np.array([c/n for c in conteo.values()])
    H = -np.sum(probs * np.log2(probs))
    return H, n

for nombre in ["Firma1Cifrada.bmp", "Firma2.bmp", "Firma3.bmp"]:
    H, n = entropia_shannon(nombre)
    print(f"{nombre:<22} entropia: {H:.4f} bits/byte (maximo teorico: 8.0)  tamano: {n} bytes")
